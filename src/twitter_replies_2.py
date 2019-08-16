import sys
import json
import time
import logging
import tweepy
from tweepy import OAuthHandler
import urllib.parse
from os import environ as e

consumer_key = 'WAfMFUeX727ZJyHbxRG5TqbHx'
consumer_secret_key = 'QempGWO01nvNXJROIBHdIPAcGsC78qCzM4XI7ZYbZEsTlL0jb2'
access_token = '1132328609270697985-o0RjHLFH5oEeNw5It2gOiJgPOPBpMD'
access_token_key = 'CmFuCC6UAZpV8GgSs5Y3pH3dGWX5x1zL6cNry2ESQT7Pr'

api = tweepy.API(authentication)

authentication = OAuthHandler(consumer_key , consumer_secret_key)
authentication.set_access_token(access_token , access_token_key)

def tweet_url(t):
    return "https://twitter.com/TheEconomist/status/1161166753017339904" 

def get_tweets(filename):
    list_of_tweets_json = []
    for line in open(filename):
        names_list = [line.strip() for line in open(filename) if line.strip()]
    for i in names_list:
        yield list_of_tweets_json.append(json.loads(i))
		#yield tweepy.Status.NewFromJsonDict(json.loads(line))

def get_replies(tweet):
    user = 'TheEconomist'
    tweet_id = '1161166753017339904'
    max_id = None
    logging.info("looking for replies to: %s" % tweet_url(tweet))
    print(user + '\n' + tweet_id + '\n')
    while True:
        q = urllib.parse.urlencode({"q": "to:TheEconomist"})
        print(q)
        replies = api.search(q="@TheEconomist",since_id='1161166753017339904', max_id = max_id, count = 100)
		print(replies)
        #replies = t.GetSearch(raw_query="to:TheEconomist", since_id=tweet_id, max_id=max_id, count=100)
        for reply in replies:
            logging.info("examining: %s" % tweet_url(reply))
            if reply.in_reply_to_status_id == tweet_id:
                logging.info("found reply: %s" % tweet_url(reply))
                yield reply
                # recursive magic to also get the replies to this reply
                for reply_to_reply in get_replies(reply):
                    yield reply_to_reply
            max_id = reply.id
        if len(replies) != 100:
            break

if __name__ == "__main__":
    logging.basicConfig(filename="replies.log", level=logging.INFO)
    tweets_file = sys.argv[1]
    print('Starting the process')
    #get_replies(tweet)
    #print(reply.AsJsonString())
    for tweet in get_tweets(tweets_file):
        print(tweet)
        for reply in get_replies(tweet):
            print(reply.AsJsonString())