import pandas as pd
import nltk
import re
import yaml
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize

parameters = {}
print('Initializing Hate Labeling...')
# read parameters:
with open("../parameters.yml", 'r') as stream:
    try:
        parameters = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def preprocess_tweet(tweet):
    text = tweet
    # Delete mentions:
    text = re.sub(r'@\w+', '', text)
    # Delete URLs:
    text = re.sub(r'http.?://[^\s]+[\s]?', '', text)
    # Delete digits and symbols such as points, hashtags, commas, etc:
    text = re.sub('[^a-zA-Z\s]', '', text)
    # Delete extra white spaces:
    # text = re.sub("\s+", '', text)
    # text = text.lstrip()
    # text = text.rstrip()
    # Make text lower-case
    text = text.lower()
    return text


def delete_stop_words(tokenized_text):
    stop_words = set(stopwords.words("english"))
    filtered_text = []
    for word in tokenized_text:
        if word not in stop_words:
            filtered_text.append(word)
    return filtered_text


def stemming_text(tokenized_text):
    ps = PorterStemmer()
    stemmed_words = []
    for word in tokenized_text:
        stemmed_words.append(ps.stem(word))
    return stemmed_words


def lemmatization_text(tokenized_text):
    lem = WordNetLemmatizer()
    lemm_words = []
    for word in tokenized_text:
        lemm_words.append(lem.lemmatize(word, "v"))
    return lemm_words


def tokenize(text):
    tokenized_text = word_tokenize(text)
    # print(tokenized_text)
    # delete stop words
    tokenized_text = delete_stop_words(tokenized_text)
    # stemming
    tokenized_text = stemming_text(tokenized_text)
    # delete stop words
    tokenized_text = lemmatization_text(tokenized_text)
    # print(tokenized_text)
    return tokenized_text


def create_tokenized_list(df):
    tweets = []
    for index, row in df.iterrows():
        # delete unnecessary characters
        # print(row['tweet'])
        text = preprocess_tweet(row['tweet'])
        # print(text)
        tokenized_text = tokenize(text)
        tweets.append((tokenized_text, row['label']))
    return tweets


def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
        all_words.extend(words)
    return all_words


def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features


def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features


# Manually classified tweets retrieved from here: https://datahack.analyticsvidhya.com
# 0 - not detected
# 1 - subject of hate speech
# why first 2000 was chosen?
print('Loading data! Please wait...')
df_labeled_tweets = pd.read_csv(parameters['dataset_directory'] + '/' + parameters['dataset_file'])
df_token_tweets = create_tokenized_list(df_labeled_tweets.head(parameters['max_power']))
word_features = get_word_features(get_words_in_tweets(df_token_tweets))
training_set = nltk.classify.apply_features(extract_features, df_token_tweets)
classifier = nltk.NaiveBayesClassifier.train(training_set)
print('Labeling is now started...')
# current index
checkLockerFile = open(parameters['process_directory'] + '/' + parameters['label_file'])
current_index = checkLockerFile.read()
index = -1
# open up the replies file
csvFile = parameters['process_directory'] + '/' + parameters['reply_file']
df_replies = pd.read_csv(csvFile, sep=',')
# drop headers
df_replies = df_replies.iloc[1:]
if 'automatic' not in df_replies.columns:
    df_replies['automatic'] = ''
if 'manual' not in df_replies.columns:
    df_replies['manual'] = ''
for index, row in df_replies.iterrows():
    if index <= int(current_index):
        continue
    elif 0 == index % parameters['refresh_lock']:
        current_index = str(index)
        # print('Process lock updated:' + current_index)
        lockerFile = open(parameters['process_directory'] + '/' + parameters['face_file'], 'w+')
        lockerFile.write(current_index)
        lockerFile.close()
        # save the processed data
        df_replies.to_csv(csvFile, index=False, header=True, sep=',', encoding='utf-8')
    # check for the hate occurrence
    tempest = preprocess_tweet(row['text'])
    tempest = tempest.replace('&comma;', ',')
    tokenized_text = tokenize(tempest)
    print(str(index) + ' xxx ' + str(classifier.classify(extract_features(tokenized_text))))
    df_replies.loc[index, 'automatic'] = classifier.classify(extract_features(tokenized_text))
    # automatic and manual have to be compared
print('Last lock index: ' + str(index))
df_replies.to_csv(csvFile, index=False, header=True, sep=',', encoding='utf-8')
print('Operation finished')
