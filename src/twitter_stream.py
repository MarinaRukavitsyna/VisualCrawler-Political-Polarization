import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import re
import pandas

consumer_key = 'gkkyZWHLaTKz0lEWgIS04aqZz'
consumer_secret_key = 'GBvbd9j4ulE1QqXRcryBTvMgD9QJvccbwAnDkdB8EjnMyfLcHz'
access_token = '1132328609270697985-hVxMrxq8ZTYLMEQYWD7rXZnqwSgIzq'
access_token_key = '889vgnfWTWQs3yFxEoGya4DTGmnMnq6HQjk80GXOI2ZV9'

class listener(StreamListener):

    def on_data(self, data):
        print(data)
        #return True
    
    def on_status(self, status):
        print(status.text)

    def on_error(self, status):
        if status == 420:
            return False
        print(status)

auth = OAuthHandler(consumer_key, consumer_secret_key)
auth.set_access_token(access_token, access_token_key)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

follow_list = ['2467791','759251','1652541','14293310','97739866','1367531','5988062','807095','3108351']
track_list=['trump','donald trump','president','donald','US Congress','angela merkel','simone','biles','simone biles','government']

twitterStream = Stream(auth, listener(), wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
twitterStream.filter(follow = follow_list, track = track_list, languages = ['en'])    