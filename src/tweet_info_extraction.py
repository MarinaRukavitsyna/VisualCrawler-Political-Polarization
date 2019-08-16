import json
import pandas as pd
import csv
import datetime

## Step 1: Load .json file into a list of json variable

list_of_tweets_json = []
with open('tweets_2_date_20190816.json', 'r') as myfile:
    names_list = [line.strip() for line in myfile if line.strip()]

for i in names_list:
    list_of_tweets_json.append(json.loads(i))
	
## Step 2: taking only those tweets that has images
list_of_tweets_with_images = []
for entity in list_of_tweets_json:
    if 'entities' in entity.keys() and 'media' in entity['entities'].keys():
        list_of_tweets_with_images.append(entity)

## Step 3: taking only those tweets that are about donald trump

list_tweets_about_string = []
check_string = ['donald','trump','donald trump']
for tweet in list_of_tweets_with_images:
    if any(x in tweet['text'] for x in check_string):
        list_tweets_about_string.append(tweet)
		
## Step 4: Extracting the tweet related info and populating a pandas dataframe:
tweets = pd.DataFrame(columns=[ 'tweet_id',
								'tweet_str_id',
								'retweet_from_tweet_str_id',
								'text',
								'hashtags',
								'user_id',
								'original_user_id',
								'created_at',
								'image_url'])

for j in list_tweets_about_string:
    
    tweets = tweets.append({'tweet_id': j['id'],
							'tweet_str_id' : j['id_str'],
                            'retweet_from_tweet_str_id' : j['retweeted_status']['id_str'] if 'retweeted_status' in j.keys() else 'None',
                            'text' : j['text'] ,
							'hashtags': j['entities']['hashtags'][0]['text'] if len(j['entities']['hashtags']) != 0 else 'None',
                            'user_id' : j['user']['screen_name'],
							'original_user_id' : j['retweeted_status']['user']['screen_name'] if 'retweeted_status' in j.keys() else 'None',
                            'created_at' : j['created_at'],
                            'image_url' : j['entities']['media'][0]['media_url']
                            }, ignore_index=True)

tweets = tweets.sort_values(by=['retweet_from_tweet_str_id', 'tweet_id','created_at'])							

## Step 5: exporting the aggregated tweet info into a .csv file:

file_name = 'tweets_'+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))+ '.csv'

with open(file_name, 'a', encoding = "utf-8") as f:
       tweets.to_csv(f, index=False)
	   
	   
	   
## Step 6: To get Replies:

replies_to_tweets = tweets[['retweet_from_tweet_str_id','original_user_id']]
replies_to_tweets = replies_to_tweets.drop_duplicates(keep='first')
replies_to_tweets = replies_to_tweets[replies_to_tweets['retweet_from_tweet_str_id'] != 'None']   

file_name = 'replies_'+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))+ '.csv'

with open(file_name, 'a', encoding = "utf-8") as f:
       tweets.to_csv(f, index=False)