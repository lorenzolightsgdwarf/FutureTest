import tweepy

auth = tweepy.OAuthHandler("",
                           "")
auth.set_access_token("",
                      "")

api = tweepy.API(auth)
public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)
result=api.search(q='puppy filter:images filter:safe',lang='it')
for tweet in result:
    print(tweet.text)