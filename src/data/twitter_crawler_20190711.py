############## Library imports ############
import tweepy
from tweepy import OAuthHandler
import re
import pandas as pd
import datetime
import urllib.request
from collections import OrderedDict
import csv
import sys
import logging

############# Step 1: Authentication #########

consumer_key = 'gkkyZWHLaTKz0lEWgIS04aqZz'
consumer_secret_key = 'GBvbd9j4ulE1QqXRcryBTvMgD9QJvccbwAnDkdB8EjnMyfLcHz'
access_token = '1132328609270697985-hVxMrxq8ZTYLMEQYWD7rXZnqwSgIzq'
access_token_key = '889vgnfWTWQs3yFxEoGya4DTGmnMnq6HQjk80GXOI2ZV9'

authentication = OAuthHandler(consumer_key , consumer_secret_key)
authentication.set_access_token(access_token , access_token_key)

api = tweepy.API(authentication)

# A Function to setup Crawler's Environment Variables such as:
# (1) time range to crawl 
# (2) twitter handles to crawl
# (3) what should the tweets contain? Trump? Brexit? Putin? etc.

def crawler_env_var_setup():
    #global list_of_twitter_handles
    #list_of_twitter_handles = ''
    with open('crawler_config_file.txt','r') as cf:
        text = cf.read().splitlines()
        
        try:
            if re.search('twitter_handles',text[3]) == True:
                print(text[3].split('|')[1])
        except:
            print('List of Twitter accounts to crawl and or tweets about filters are empty!! Please check if crawler_config_file.txt exists and has valid data. Exiting the program')
            sys.exit(1)
        
        start_time = datetime.datetime.strptime(text[0].split('|')[1], '%Y-%m-%d %H:%M:%S') if re.search('starttime',text[0]) else ''
        end_time = datetime.datetime.strptime(text[1].split('|')[1], '%Y-%m-%d %H:%M:%S') if re.search('endtime',text[1]) else ''
        tweets_about = text[2].split('|')[1] if re.search('tweets_about',text[2]) else ''
        list_of_twitter_handles = text[3].split('|')[1] if re.search('twitter_handles',text[3]) else ''
    return[str(start_time), str(end_time), str(tweets_about), str(list_of_twitter_handles)]

# A Function to :
# (1) create a csv file of tweet information
# (2) Download images in the tweet

def get_images_and_csv():
    file_name = 'tweet_info_'+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + '.csv'
    with open(file_name, 'a', encoding = "utf-8") as f:
        tweet_info.to_csv(f, index=False)
    #importing all the images:

    image_list = pd.read_csv(file_name,usecols=['tweet_id','image_url']).dropna()
    id_img = pd.Series(image_list.image_url.values,index=image_list.tweet_id).to_dict()
    id_img = OrderedDict(id_img)
    
    for i,j in id_img.items():
        fn = image_list['tweet_id']
        fn = i
        urllib.request.urlretrieve(j,str(fn)+'.jpg') #downloading images with tweet_id as filename

#############################################################################################################

# setting up the crawler parameters to use the ones mentioned in crawler_config_file.txt        
carwler_var = crawler_env_var_setup()

start_date = datetime.datetime.strptime(carwler_var[0],'%Y-%m-%d %H:%M:%S')
end_date = datetime.datetime.strptime(carwler_var[1],'%Y-%m-%d %H:%M:%S')
tweets_about = carwler_var[2].lower().split(',')
list_of_twitter_handles = carwler_var[3].split(',')
#tweets_about.append('is')
print(str(start_date) + '\n' + str(end_date) + '\n' + str(tweets_about) + '\n' + str(list_of_twitter_handles))

#variable declarations

tweets = []
status = []
med={} # media- image urls

#creating empty dataframe to populate with tweet info
tweet_info = pd.DataFrame(columns = ['tweet_id','retweet_from_id','tweet_text','hashtags','user_id','created_ts','image_url'])

#creating an empty csv file with headers if it doesn't exist already. Otherwise append in 

#Final csv file config:

try:
    with open('twitter_info.csv','r'):
        print('file exists already')
except:
    with open('twitter_info.csv','w') as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(["tweet_id" , "retweet_from_id" , "tweet_text", "hastags", "user_id", "created_ts", "image_url"])
    
############################################################################################################

for handle in list_of_twitter_handles:
    #support pagination and retrieve upto 3.2k tweets
    #print(handle.replace('\'',''))
    for statuses in tweepy.Cursor(api.user_timeline, screen_name = handle.replace('\'',''), tweet_mode="extended").items(2):
        status.append(statuses)
        
    # filter on timeframe and keyword texts  
    #for j in status: 
     #   for k in tweets_about:
      #      if j.created_at >= start_date and j.created_at <= end_date and str(k) in j.full_text.lower(): 
       #         tweets.append(j)

    for j in status:
        if j.created_at >= start_date and j.created_at <= end_date:
            tweets.append(j)
        
    #tweets = list(dict.fromkeys(tweets))
    
# populate df with required info re tweet
    for i in tweets:
        #print(i)
        med.clear()
        if 'media' in i.entities:
            med = i.extended_entities['media'][0]
        tweet_info = tweet_info.append({'tweet_id': i._json['id'], 
                                        'retweet_from_id': str(i).split()[1].strip("@:") if i._json['full_text'].startswith('RT @') else '',
                                        'tweet_text': i._json['full_text'],
                                        'hashtags': i.entities['hashtags'][0]['text'] if bool(i.entities['hashtags']) == True else '',
                                        'user_id': i._json['user']['screen_name'],
                                        'created_ts': i._json['created_at'],
                                        'image_url': med['media_url'] if 'media_url' in med else ''}, ignore_index=True)

tweet_info = tweet_info[tweet_info.image_url != ''] #ignoring tweets without images

tweet_info = tweet_info.drop_duplicates(keep = 'first')  # all tweet info and img url, except replies to tweets are present here to create csv file.

get_images_and_csv()

############################################################################################################


# comments

comments = pd.DataFrame(columns=['id','replies'])

for i in tweet_info['user_id']:
    for mentions in tweepy.Cursor(api.search, q=i).items(50):
        comments = comments.append({'id': mentions._json['in_reply_to_status_id'],
                                   'replies': mentions._json['text']}, ignore_index=True)
        #print(mentions._json['id'] + mentions._json['text'])
    
comments = comments.drop_duplicates(keep = 'first')

file_name = 'tweet_comments_'+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + '.csv'
with open(file_name, 'a', encoding = "utf-8") as f:
       comments.to_csv(f, index=False)
