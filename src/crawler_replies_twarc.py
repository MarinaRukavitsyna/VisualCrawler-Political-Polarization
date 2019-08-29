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
import subprocess


parameters = {}
print('Initializing Reply Collector...')
print('** Do not forget to configure twarc ($twarc config)!')
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


if __name__ == "__main__":
    logging.basicConfig(filename=parameters['log_directory'] + '/' + "replies.log", level=logging.INFO)
    checkLockerFile = open(parameters['process_directory'] + '/' + parameters['lock_file'])
    current_index = checkLockerFile.read()
    csvFile = parameters['process_directory'] + '/' + parameters['parsed_file']
    print('Starting from last locked row: ' + current_index)

    with open(csvFile) as my_csv:
        rows = csv.reader(my_csv, delimiter=',')
        index = -1
        for index, element in enumerate(rows):
            if index <= int(current_index):
                continue
            elif 0 == index % parameters['refresh_lock']:
                # update lock
                current_index = str(index)
                print('Process lock updated:' + current_index)
                lockerFile = open(parameters['process_directory'] + '/' + parameters['lock_file'], 'w+')
                lockerFile.write(current_index)
                lockerFile.close()
            # proceed for original tweets only:
            tweet_id = element[0]
            if '' != element[len(element)-2] and '0' != element[len(element)-2]:
                print('Processing ' + tweet_id)
                # seems better with no recursion active
                out = subprocess.Popen(['twarc', 'replies', str(element[0])],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
                replies, errors = out.communicate()
                replies = replies.decode("utf-8")
                my_reply_list = pd.DataFrame(columns=['tweet_id',
                                                      'reply_id',
                                                      'reply_to_reply_id',
                                                      'hashtags',
                                                      'country',
                                                      'location_full_name',
                                                      'user_id',
                                                      'text',
                                                      'created_at',
                                                      'user_friends_count',
                                                      'user_follower_count',
                                                      'user_location',
                                                      ])
                for tempest_line in replies.splitlines():
                    if '' == tempest_line or '\n' == tempest_line:
                        continue
                    parsed_json = (json.loads(tempest_line))
                    print(parsed_json)
                    # save all replies anyways
                    temper = {
                        'country': '',
                        'full_name': '',
                        'user_location': '',
                        'friends_count': '',
                        'followers_count': '',
                    }
                    try:
                        temper['country'] = parsed_json['place']['country']
                    except:
                        pass
                    try:
                        temper['full_name'] = parsed_json['place']['full_name']
                    except:
                        pass
                    try:
                        temper['user_location'] = parsed_json['user']['location']
                    except:
                        pass
                    try:
                        temper['friends_count'] = parsed_json['user']['friends_count']
                    except:
                        pass
                    try:
                        temper['followers_count'] = parsed_json['user']['followers_count']
                    except:
                        pass
                    full_text = parsed_json['full_text'].replace(',', '&comma;')
                    my_reply_list = my_reply_list.append({
                        'tweet_id': tweet_id,
                        'reply_id': parsed_json['id'],
                        'reply_to_reply_id': parsed_json['in_reply_to_user_id'],
                        'hashtags': parsed_json['entities']['hashtags'],
                        'country': temper['country'],
                        'location_full_name': temper['full_name'],
                        'user_id': parsed_json['user']['id'],
                        'user_friends_count': temper['friends_count'],
                        'user_follower_count': temper['followers_count'],
                        'user_location': temper['user_location'],
                        'text': full_text,
                        'created_at': parsed_json['created_at'],
                    }, ignore_index=True)

                is_header_active = not os.path.exists(parameters['process_directory'] + '/' + parameters['reply_file'])
                with open(parameters['process_directory'] + '/' + parameters['reply_file'], 'a', encoding="utf-8") as f:
                    my_reply_list.to_csv(f, header=is_header_active, index=False)

                if errors is not None:
                    print('Collecting data faced an error ' + str(errors))

        print('Operation finished')
        print('Last lock index: ' + str(index))
        lockerFile = open(parameters['process_directory'] + '/' + parameters['lock_file'], 'w+')
        lockerFile.write(str(index))
        lockerFile.close()
