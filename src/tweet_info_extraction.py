########################### Twitter Object JSON processing to create csv file #######################
import json
import pandas as pd
import csv
import datetime
import sys

## Step 1: Load .json file into a list of json variable
json_file_name = str(sys.argv[1:][0])
print('processing the file: ' +  json_file_name + '\n')
list_of_tweets_json = []

#with open('tweets_date_20190818.json', 'r') as myfile:
 #   names_list = [line.strip() for line in myfile if line.strip()]
	
with open(json_file_name, 'r') as myfile:
    names_list = [line.strip() for line in myfile if line.strip()] #removing blank lines

print('number of tweets: ' + str(len(names_list)) + '\n')
# looping through each twitter object.
for i in names_list:
    list_of_tweets_json.append(json.loads(i))
	
## Step 2: taking only those tweets that has images
list_of_tweets_with_images = []
for entity in list_of_tweets_json:
    if 'entities' in entity.keys() and 'media' in entity['entities'].keys():
        list_of_tweets_with_images.append(entity)

print('number of tweets with images: ' + str(len(list_of_tweets_with_images)) + '\n')

## Step 3: taking only those tweets that are about donald trump

list_tweets_about_string = []
check_string = ['donald','trump','donald trump']
for tweet in list_of_tweets_with_images:
    txt = tweet['text'].lower()
    if any(x in txt for x in check_string):     
        list_tweets_about_string.append(tweet)

print('number of tweets about Donald Trump: ' + str(len(list_tweets_about_string)) + '\n')
		
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
								
replies = pd.DataFrame(columns=[ 'tweet_id',
								'original_user_id'])
								
#for j in list_of_tweets_with_images:
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

    replies = replies.append({'tweet_id': j['id'],
							'original_user_id' : j['retweeted_status']['user']['screen_name'] if 'retweeted_status' in j.keys() else 'None'
                            }, ignore_index=True)
							
tweets = tweets.sort_values(by=['retweet_from_tweet_str_id', 'tweet_id','created_at'])							

reply = replies[replies['original_user_id'] != 'None'].set_index('tweet_id').T.to_dict('list')

## Step 5: exporting the aggregated tweet info into a .csv file:

file_name = 'tweets_'+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))+ '.csv'

with open(file_name, 'a', encoding = "utf-8") as f:
       tweets.to_csv(f, index=False)
	   
	   
file_name = 'reply_for_tweets_'+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))+ '.json'
with open(file_name, 'a') as f:
    for i in reply:
        screen_name = reply[i][0]
        uid = i
        f.write('{"user":{"screen_name": "' + screen_name + '"},"id":' + str(uid) + '}'+'\n') 
		

	   
	   