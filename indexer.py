import tweepy
from datetime import datetime
from elasticsearch import Elasticsearch
import fileinput
MAX_TWEETS = 100 # Highest limit which Twitter API allows


es = Elasticsearch()

inputList = list()
for line in fileinput.input("twitterKeys"):     # read API-keys for twitter from file. This file is not stored on github.
    inputList.append(line.rstrip())

consumer_key = inputList[0]
consumer_secret = inputList[1]
access_token = inputList[2]
access_token_secret = inputList[3]


auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth,  wait_on_rate_limit=True) # wait_on_rate_limit causes tweepy to be blocking if the twitter API rate limit is hit. This simplifies our code.

i = 0
while True:
    break
    query = raw_input()

    public_tweets = api.search(q=query, lang='en', count=MAX_TWEETS, tweet_mode='extended') # tweet_mode=extended allows for retireval of long length tweets as well
    for tweet in public_tweets:
        full_text_retweeted = tweet._json.get("retweeted_status")   # Due to irregularities in the twitter API, a retweeted, extended length tweet has to be retireved from the original tweet.
        if None != full_text_retweeted:
            docID = full_text_retweeted.get("id")
            doc = { 'author': full_text_retweeted.get("user").get("name"), # Grab the docID, author, tweet text, and the timestamp for the tweet and index them
                'text': full_text_retweeted.get("full_text"),
                'datestamp': full_text_retweeted.get("created_at")
                }
            es.index(index="twitter", doc_type='tweet', id=docID, body=doc)
        else:                                       # Same as above, but for cases where the tweet has not been retweeted
            docID = tweet.id
            doc = { 'author': tweet.user.name,
                'text': tweet.full_text,
                'datestamp': tweet.created_at
                }
            es.index(index="twitter", doc_type='tweet', id=docID, body=doc)
    i+=1
    if i % 5 == 0:
        print(str(i) + " , word: " + query) # Prints every 5th api request just to see that request are being handled
