import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import re
import pandas

consumer_key = 'WAfMFUeX727ZJyHbxRG5TqbHx'
consumer_secret_key = 'QempGWO01nvNXJROIBHdIPAcGsC78qCzM4XI7ZYbZEsTlL0jb2'
access_token = '1132328609270697985-o0RjHLFH5oEeNw5It2gOiJgPOPBpMD'
access_token_key = 'CmFuCC6UAZpV8GgSs5Y3pH3dGWX5x1zL6cNry2ESQT7Pr'

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
