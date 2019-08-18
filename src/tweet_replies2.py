import sys
import json
import time
import logging
import twitter
import urllib.parse
import re
import csv
import pandas as pd
import datetime

from os import environ as e

e["CONSUMER_KEY"]="WAfMFUeX727ZJyHbxRG5TqbHx"
e['CONSUMER_SECRET']="QempGWO01nvNXJROIBHdIPAcGsC78qCzM4XI7ZYbZEsTlL0jb2"
e["ACCESS_TOKEN"]="1132328609270697985-o0RjHLFH5oEeNw5It2gOiJgPOPBpMD"
e['ACCESS_TOKEN_SECRET']="CmFuCC6UAZpV8GgSs5Y3pH3dGWX5x1zL6cNry2ESQT7Pr"

t = twitter.Api(
    consumer_key=e["CONSUMER_KEY"],
    consumer_secret=e["CONSUMER_SECRET"],
    access_token_key=e["ACCESS_TOKEN"],
    access_token_secret=e["ACCESS_TOKEN_SECRET"],
    sleep_on_rate_limit=True
)

def tweet_url(t):
    return "https://twitter.com/%s/status/%s" % (t.user.screen_name, t.id)

def get_tweets(filename):
    for line in open(filename):
        yield twitter.Status.NewFromJsonDict(json.loads(line))

def get_replies(tweet):
    f= open("tweet_replies_2.txt","a+",encoding="utf-8")
    f2= open("tweet_replies_to_status.txt","a+",encoding="utf-8")
    user = tweet.user.screen_name
    tweet_id = tweet.id
    max_id = None
    logging.info("looking for replies to: %s" % tweet_url(tweet))
    while True:
        q = urllib.parse.urlencode({"q": "to:%s" % user})
        print(str(q))
        try:
            replies = t.GetSearch(raw_query=q, since_id=tweet_id, max_id=max_id, count=100)
            f.write(str(replies)+'\n') 
#            print(str(replies))
        except twitter.error.TwitterError as e:
            logging.error("caught twitter api error: %s", e)
            time.sleep(60)
            continue
        for reply in replies:
            logging.info("examining: %s" % tweet_url(reply))
            if reply.in_reply_to_status_id == tweet_id:
                logging.info("found reply: %s" % tweet_url(reply))
                f2.write(str(reply)) 
                yield reply
                # recursive magic to also get the replies to this reply
                for reply_to_reply in get_replies(reply):
                    yield reply_to_reply
            max_id = reply.id
        if len(replies) != 100:
            break

def replies_export():
    list_of_replies_json = []

    with open("tweet_replies_to_status.txt", 'r',encoding="utf-8") as myfile:
        for i in myfile.readlines():
            list_of_replies_json.append(i)
    
            replies = pd.DataFrame(columns=[ 'tweet_id',
                                'text',
                                'user_id']) 
        
            for j in list_of_replies_json:
                #print(j)
                replies = replies.append({'tweet_id': re.search('Status\(ID=(.+?),', j).group(1),
                            'text' : re.search('Text=(.+?),', j).group(1),
                            'user_id' : re.search('ScreenName=(.+?),', j).group(1)
                            }, ignore_index=True)
                replies = replies.sort_values(by=['tweet_id'])
                replies = replies.drop_duplicates(subset ="text", 
                     keep = 'first', inplace = True)
            file_name = 'replies_'+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))+ '.csv'

    with open(file_name, 'a', encoding = "utf-8") as f:
        replies.to_csv(f, index=False)
	   
if __name__ == "__main__":
    logging.basicConfig(filename="replies.log", level=logging.INFO)
    tweets_file = sys.argv[1]
    for tweet in get_tweets(tweets_file):
        for reply in get_replies(tweet):
            print(reply.AsJsonString())
        #replies_export()  