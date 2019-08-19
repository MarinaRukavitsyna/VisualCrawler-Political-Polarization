import json
import time
import logging
import twitter
import urllib.parse
import re
import yaml
import pandas as pd
import datetime
import csv
import os
from os import environ as e

parameters = {}
print('Initializing Reply Collector...')
# read parameters:
with open("../parameters.yml", 'r') as stream:
    try:
        parameters = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

e["CONSUMER_KEY"] = parameters['consumer_key']
e['CONSUMER_SECRET'] = parameters['consumer_secret_key']
e["ACCESS_TOKEN"] = parameters['access_token']
e['ACCESS_TOKEN_SECRET'] = parameters['access_token_key']

t = twitter.Api(
    consumer_key=e["CONSUMER_KEY"],
    consumer_secret=e["CONSUMER_SECRET"],
    access_token_key=e["ACCESS_TOKEN"],
    access_token_secret=e["ACCESS_TOKEN_SECRET"],
    sleep_on_rate_limit=True
)


def tweet_url(t):
    return "https://twitter.com/%s/status/%s" % (t.user.screen_name, t.id)


def get_tweets(temp_conditions):
    yield twitter.Status.NewFromJsonDict(json.loads(temp_conditions))


def get_replies(tweet_element):
    user = tweet_element.user.screen_name
    tweet_id = tweet_element.id
    max_id = None
    logging.info("looking for replies to: %s" % tweet_url(tweet_element))

    my_reply_list = pd.DataFrame(columns=['tweet_id',
                                          'reply_id',
                                          'hashtags',
                                          'country',
                                          'location_full_name',
                                          'user_id',
                                          'text',
                                          'created_at',
                                          'user_friends_count',
                                          'user_follower_count',
                                          'user_location'
                                          ])

    while True:
        q = urllib.parse.urlencode({"q": "to:%s" % user})
        # print(str(q))
        try:
            replies = t.GetSearch(raw_query=q, since_id=tweet_id, max_id=max_id, count=100)
        except twitter.error.TwitterError as e:
            logging.error("caught twitter api error: %s", e)
            time.sleep(60)
            continue
        for tempest_reply in replies:
            logging.info("examining: %s" % tweet_url(tempest_reply))
            if tempest_reply.in_reply_to_status_id == tweet_id:
                logging.info("found reply: %s" % tweet_url(tempest_reply))
                parsed_json = (json.loads(str(tempest_reply)))
                my_reply_list = my_reply_list.append({
                    'tweet_id': tweet_id,
                    'reply_id': parsed_json['id'],
                    'hashtags': parsed_json['hashtags'],
                    'country': parsed_json['place']['country'],
                    'location_full_name': parsed_json['place']['full_name'],
                    'user_id': parsed_json['user']['id'],
                    'user_friends_count': parsed_json['user']['friends_count'],
                    'user_follower_count': parsed_json['user']['followers_count'],
                    'user_location': parsed_json['user']['location'],
                    'text': parsed_json['text'],
                    'created_at': parsed_json['created_at']
                }, ignore_index=True)
                yield tempest_reply
                # recursive magic to also get the replies to this reply
                for reply_to_reply in get_replies(tempest_reply):
                    yield reply_to_reply
            max_id = tempest_reply.id
        if len(replies) != 100:
            break

    is_header_active = not os.path.exists(parameters['process_directory'] + '/' + parameters['reply_file'])
    with open(parameters['process_directory'] + '/' + parameters['reply_file'], 'a', encoding="utf-8") as f:
        my_reply_list.to_csv(f, header=is_header_active, index=False)


def replies_export():
    list_of_replies_json = []

    with open(parameters['log_directory'] + '/' + "tweet_replies_to_status.txt", 'r', encoding="utf-8") as my_file:
        for i in my_file.readlines():
            list_of_replies_json.append(i)

            replies = pd.DataFrame(columns=['tweet_id',
                                            'text',
                                            'user_id'])

            for j in list_of_replies_json:
                # print(j)
                replies = replies.append({'tweet_id': re.search('Status\(ID=(.+?),', j).group(1),
                                          'text': re.search('Text=(.+?),', j).group(1),
                                          'user_id': re.search('ScreenName=(.+?),', j).group(1)
                                          }, ignore_index=True)
                replies = replies.sort_values(by=['tweet_id'])
                replies = replies.drop_duplicates(subset="text",
                                                  keep='first', inplace=True)
            file_name = 'replies_' + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + '.csv'

    with open(file_name, 'a', encoding="utf-8") as f:
        replies.to_csv(f, index=False)


if __name__ == "__main__":
    logging.basicConfig(filename=parameters['log_directory'] + '/' + "replies.log", level=logging.INFO)
    checkLockerFile = open(parameters['process_directory'] + '/' + parameters['lock_file'])
    current_index = checkLockerFile.read()
    csvFile = parameters['process_directory'] + '/' + parameters['parsed_file']
    print('Starting from last locked row: ' + current_index)
    with open(csvFile) as my_csv:
        rows = csv.reader(my_csv, delimiter=',')
        index = 0
        for index, element in enumerate(rows):
            if index <= int(current_index):
                continue
            elif 0 == index % parameters['refresh_lock']:
                # update lock
                print(current_index)
                current_index = str(index)
                lockerFile = open(parameters['process_directory'] + '/' + parameters['lock_file'], 'w+')
                lockerFile.write(current_index)
                lockerFile.close()
            # {"user":{"screen_name": "RT_com"},"id":1163141231075090432}
            conditions = '{"user":{"screen_name": "' + element[5] + '"},"id":' + str(element[0]) + '}'
            for tweet in get_tweets(conditions):
                for reply in get_replies(tweet):
                    pass

        lockerFile = open(parameters['process_directory'] + '/' + parameters['lock_file'], 'w+')
        lockerFile.write(str(index))
        lockerFile.close()
