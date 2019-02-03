from re import split

import tweepy
from lxml import html
import requests
import urllib.request
import time
import pathlib
import sys
import json


def process_results(results):
    for tweet in results:
        pic_url = ''
        if 'media' in tweet.entities:
            medias = tweet.entities['media']
            if len(medias) > 0:
                pic_url = medias[0]['media_url']
        if pic_url == '' and 'urls' in tweet.entities:
            if len(tweet.entities['urls']) > 0:
                external_url = tweet.entities['urls'][0]['expanded_url']
                page = requests.get(external_url)
                page_tree = html.fromstring(page.content)
                pics = page_tree.xpath('//div[contains(@class,"AdaptiveMedia-photoContainer")]')
                if len(pics) > 0:
                    pic_url = pics[0].attrib['data-image-url']
        if pic_url != '':
            split_str = pic_url.split('.')
            pic_name = 'data/' + str(tweet.id) + '.' + split_str[len(split_str) - 1]
            urllib.request.urlretrieve(pic_url, pic_name)
            text_file_name = 'data/' + str(tweet.id) + '.txt'
            file = open(text_file_name, 'w', encoding="utf-8")
            file.write(tweet.full_text)
            file.close()
    return;


def update_intervals(results):
    global upper_bound
    global lower_bound
    global current_cursor
    for tweet in results:
        if upper_bound is None or tweet.id > upper_bound:
            upper_bound = tweet.id
    if hasattr(results, "max_id"):
        current_cursor = results.max_id - 1
    else:
        current_cursor = None
        lower_bound = upper_bound
        upper_bound = None
    return;


def load_search_data():
    global upper_bound
    global lower_bound
    global current_cursor
    stored_data_path = pathlib.Path('stored_data.json')
    if stored_data_path.is_file():
        stored_data_file = open("stored_data.json", 'r')
        stored_data = json.load(stored_data_file)
        upper_bound = stored_data['upper_bound']
        lower_bound = stored_data['lower_bound']
        current_cursor = stored_data['current_cursor']
    return;


def save_search_data():
    global upper_bound
    global lower_bound
    global current_cursor
    data2store = {
        'upper_bound': upper_bound,
        'lower_bound': lower_bound,
        'current_cursor': current_cursor
    }

    with open("stored_data.json", "w") as write_file:
        json.dump(data2store, write_file)
    return;


pathlib.Path('data').mkdir(parents=True, exist_ok=True)

exec(open("./credentials.py").read())

api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
loop = True
lower_bound = 0
upper_bound = None
current_cursor = None
query = 'puppy filter:twimg filter:safe -filter:retweets'
load_search_data()

while loop:
    print("Lower:" + str(lower_bound))
    print("Current:" + str(current_cursor))
    print("Upper:" + str(upper_bound))
    results = api.search(q=query, lang='en', max_id=current_cursor,
                         tweet_mode='extended', since_id=lower_bound)

    if not results:
        print("Empty Results")
        time.sleep(30 * 60)
    else:
        process_results(results)
        update_intervals(results)
        save_search_data()
