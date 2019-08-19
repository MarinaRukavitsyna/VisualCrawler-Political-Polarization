# packages
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import yaml
import datetime
from random import randint


def random_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


parameters = {}
print('Initializing Crawler...')
# read parameters:
with open("../parameters.yml", 'r') as stream:
    try:
        parameters = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# initializing auth keys
consumer_key = parameters['consumer_key']
consumer_secret_key = parameters['consumer_secret_key']
access_token = parameters['access_token']
access_token_key = parameters['access_token_key']

# manage file name:
now = datetime.datetime.now()
dateString = now.strftime("%Y-%m-%d")
fileName = 'raw_' + dateString + '_' + str(random_digits(5)) + '.txt'
crawlFile = open(parameters['crawl_directory'] + '/' + fileName, "a")
print('Crawl File is called ' + fileName)


# overriding class definitions
class Listener(StreamListener):

    def on_data(self, data):
        crawlFile.write(data)

    def on_status(self, status):
        print('CRAWL STATUS CHANGE!')
        print(status.text)

    def on_error(self, status):
        if status == 420:
            return False
        print('CRAWL ERROR: ' + status)


# authentication
auth = OAuthHandler(consumer_key, consumer_secret_key)
auth.set_access_token(access_token, access_token_key)

# api instance creation
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

# The below list comprises of Twitter User ID corresponding to each newspaper user screen name Eg.,
# 759251 is the twitter user id of screen name 759251. More can be added to the list by simply looking
# up at http://gettwitterid.com/?user_name=CNN&submit=GET+USER+ID
print('Loading Handles! ')
follow_list = parameters['t_handles']
# track_list=['trump','donald trump','president','donald','US Congress','angela merkel','government']

# starting the twitter stream
print('Crawler is ACTIVE')
twitterStream = Stream(auth, Listener(), wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
# twitterStream.filter(follow = follow_list, track = track_list, languages = ['en'])
# track and follow do not work as AND!!!

#  Filtering the stream to include results from newspaper handles alone
twitterStream.filter(follow=follow_list, languages=['en'])
crawlFile.close()
print('Crawler is FINISHED')
