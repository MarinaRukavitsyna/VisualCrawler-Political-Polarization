#************* Twitter Crawler *******************#

############## Library imports ############
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import re
import pandas as pd
import datetime
import urllib.request
from collections import OrderedDict

############# Step 1: Authentication #########

consumer_key = 'gkkyZWHLaTKz0lEWgIS04aqZz'
consumer_secret_key = 'GBvbd9j4ulE1QqXRcryBTvMgD9QJvccbwAnDkdB8EjnMyfLcHz'
access_token = '1132328609270697985-hVxMrxq8ZTYLMEQYWD7rXZnqwSgIzq'
access_token_key = '889vgnfWTWQs3yFxEoGya4DTGmnMnq6HQjk80GXOI2ZV9'

authentication = OAuthHandler(consumer_key , consumer_secret_key)
authentication.set_access_token(access_token , access_token_key)

api = tweepy.API(authentication)

############ Step 2: Tweet Info Bifurcation ########

tweets = []
status = []
med={} # image urls
#list_of_twitter_handles = open('newspaper_list.txt','r',encoding = "utf-8") #list of screen_names to crawl

list_of_twitter_handles = ['@timesofindia','@ocregister','@TIME','@TheEconomist','@northjersey','@njdotcom']

#timeframe of tweets to filter
start_date = datetime.datetime(2019,6,22,0,0,0 ) 
end_date = datetime.datetime(2019,6,23,23,59,59 )

#creating empty dataframe to populate with tweet info
tweet_info = pd.DataFrame(columns = ['tweet_id','retweet_from_id','tweet_text','hashtags','user_id','created_ts','image_url'])

#for handle in list_of_twitter_handles.readlines():
for handle in list_of_twitter_handles:
    #support pagination and retrieve upto 3.2k tweets
    for statuses in tweepy.Cursor(api.user_timeline, screen_name = handle, tweet_mode="extended").items(10):
        status.append(statuses)
        
    # filter on timeframe   
    for j in status:   
        if j.created_at >= start_date and j.created_at <= end_date: 
            tweets.append(j)
    
    # populate df with required info re tweet
    for i in tweets:
        med.clear()
        if 'media' in i.entities:
            med = i.extended_entities['media'][0]
        tweet_info = tweet_info.append({'tweet_id': i._json['id'], 
                                        'retweet_from_id': str(i).split()[1].strip("@:") if i._json['full_text'].startswith('RT @') else '',
                                        'tweet_text': i._json['full_text'].strip("RT @:"),
                                        'hashtags': i.entities['hashtags'][0]['text'] if bool(i.entities['hashtags']) == True else '',
                                        'user_id': i._json['user']['screen_name'],
                                        'created_ts': i._json['created_at'],
                                        'image_url': med['media_url'] if 'media_url' in med else ''}, ignore_index=True)

#Appending to a csv file
with open('tweet_info.csv', 'a', encoding = "utf-8") as f:
    tweet_info.to_csv(f, index=False)
    
#importing all the images:

image_list = pd.read_csv('tweet_info.csv',usecols=['tweet_id','image_url']).dropna()
id_img = pd.Series(image_list1.image_url.values,index=image_list1.tweet_id).to_dict()
id_img = OrderedDict(id_img)

for i,j in id_img.items():
    
    fn = image_list1['tweet_id']
    fn = i
    urllib.request.urlretrieve(j,str(fn)+'.jpg') #downloading images with tweet_id as filename
    