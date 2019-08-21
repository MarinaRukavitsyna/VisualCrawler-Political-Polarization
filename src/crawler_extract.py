import json
import pandas as pd
import yaml
import glob
import sys
import os
import urllib.request

parameters = {}
print('Initializing Parser...')
# read parameters:
with open("../parameters.yml", 'r') as stream:
    try:
        parameters = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# list of available files:
files = glob.glob(parameters['crawl_directory'] + '/' + 'raw_*.txt')
# list of already processed files:
historyFile = open(parameters['process_directory'] + '/' + parameters['memory_file'])
processedList = historyFile.read().splitlines()
historyFile.close()
json_file_name = ''
for file in files:
    relativeName = file.split('/')[-1]
    if relativeName in processedList:
        continue
    else:
        json_file_name = relativeName
        break
if '' == json_file_name:
    print('Parser has no new file!')
    sys.exit(os.EX_NOINPUT)

# Step 1: Load .json file into a list of json variable
print('processing the file: ' + json_file_name + '\n')
list_of_tweets_json = []

with open(parameters['crawl_directory'] + '/' + json_file_name, 'r') as my_file:
    names_list = [line.strip() for line in my_file if line.strip()]  # removing blank lines

print('number of tweets: ' + str(len(names_list)) + '\n')
# looping through each twitter object.
for i in names_list:
    list_of_tweets_json.append(json.loads(i))

# Step 2: taking only those tweets that has images
list_of_tweets_with_images = []
for entity in list_of_tweets_json:
    if 'entities' in entity.keys() and 'media' in entity['entities'].keys():
        list_of_tweets_with_images.append(entity)

print('number of tweets with images: ' + str(len(list_of_tweets_with_images)) + '\n')

data = list_of_tweets_with_images

# Step 4: Extracting the tweet related info and populating a pandas dataframe:
tweets = pd.DataFrame(columns=['tweet_id',
                               'tweet_str_id',
                               'retweet_from_tweet_str_id',
                               'text',
                               'hashtags',
                               'user_id',
                               'original_user_id',
                               'created_at',
                               'image_url',
                               'image_name'
                               ])

replies = pd.DataFrame(columns=['tweet_id',
                                'original_user_id'])
# check previous main tweet id to avoid re-download of same images
prevTweetId = ''
imageName = ''
for j in data:
    # download images: we just grab the first image
    imageURL = j['entities']['media'][0]['media_url']
    key = j['retweeted_status']['id_str'] if 'retweeted_status' in j.keys() else 'None'
    try:
        # if 'None' == key or  True== parameters['overrule_images']:
        imageName = 'image_' + str(j['id']) + '.' + imageURL.split('.')[-1]
        urllib.request.urlretrieve(imageURL, parameters['image_directory'] + '/' + imageName)
        prevTweetId = key
    except:
        print('Parser Error! Can not download: ' + imageURL)
    textOfTweet = j['text'].replace(',', '&comma;')
    # grab tweet data
    tweets = tweets.append({'tweet_id': j['id'],
                            'tweet_str_id': j['id_str'],
                            'retweet_from_tweet_str_id': key,
                            'text': textOfTweet,
                            'hashtags': j['entities']['hashtags'][0]['text'] if len(
                                j['entities']['hashtags']) != 0 else 'None',
                            'user_id': j['user']['screen_name'],
                            'original_user_id': j['retweeted_status']['user']['screen_name'] if
                            'retweeted_status' in j.keys() else 'None',
                            'created_at': j['created_at'],
                            'image_url': j['entities']['media'][0]['media_url'],
                            'image_name': imageName
                            }, ignore_index=True)

tweets = tweets.sort_values(by=['retweet_from_tweet_str_id', 'tweet_id', 'created_at'])
# Step 5: exporting the aggregated tweet info into a .csv file:
isHeaderActive = not os.path.exists(parameters['process_directory'] + '/' + parameters['parsed_file'])
with open(parameters['process_directory'] + '/' + parameters['parsed_file'], 'a', encoding="utf-8") as f:
    tweets.to_csv(f, header=isHeaderActive, index=False)

# save file as processed:
historyFile = open(parameters['process_directory'] + '/' + parameters['memory_file'], 'a')
historyFile.write(json_file_name + '\n')
historyFile.close()
