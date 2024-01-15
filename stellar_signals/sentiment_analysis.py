import collections
from resources.ticker_universe import secmaster_ticker_list
from resources.logger_setup import get_logger
from resources.api_secrets import *
from datetime import datetime
import tensorflow as tf
import requests as r
import pandas as pd
import numpy as np
import string
import boto3
import json
import nltk
import ssl
import re


class SentimentAnalysis:
    def __init__(self) -> None:
        self.logger = get_logger()
        self.headers = {'Content-Type': 'application/json'}
        self.curr_date = datetime.now().strftime("%Y-%m-%d")
        self.tiingo_base_url = tiingo_base_url
        self.tiingo_api_key = tiingo_api_key
        self.headlines = collections.defaultdict(list)

    def get_news(self, ticker):
        try:
            url = self.tiingo_base_url + f'/tiingo/news?tickers={ticker}&token={self.tiingo_api_key}'
            res = r.get(url=url, headers=self.headers).json()
            for entry in res:
                self.headlines[ticker].append(entry['title'])
        except Exception as e:
            self.logger.exception(e)
            print(e)


    def setup(self):
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')

    def preprocess(self, df):
        print(df)
        df = self.make_lowercase(df)
        df = self.remove_punctuation(df)
        df['headline'] = df['headline'].apply(self.remove_special_characters)
        df = self.lemmatize(df)
        df['headline'] = self.convert_to_numbers(df)
        df['headline'] = df['headline'].apply(self.combine_inner_arrays)
        df['headline'] = self.pad_inner_array(df)
        df_numpy = np.vstack( df['headline'] )
        return df_numpy

    
    def make_lowercase(self, df):
        df['headline'] = df['headline'].str.lower()
        return df
    
    def remove_punctuation(self, df):
        # Create a translation table to remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        df['headline'] = df['headline'].str.translate(translator)
        return df

    # Remove special characters
    def remove_special_characters(self, sentence):
        # Use regex to remove non-alphanumeric characters
        cleaned_sentence = re.sub(r'[^A-Za-z0-9 ]+', '', sentence)
        return cleaned_sentence
    
    def lemmatize(self, df):
        # Lemmatize
        lemmatizer = nltk.stem.WordNetLemmatizer()
        df['headline'] = df['headline'].str.split()
        # Remove stopwords
        stop_words = set(nltk.corpus.stopwords.words("english"))
        df['headline'] = [[word for word in tokens if word.lower() not in stop_words] for tokens in df['headline']]
        df['headline'] = df['headline'].apply( lambda x: [lemmatizer.lemmatize(word) for word in x] )
        df['headline'] = df['headline'].apply(self._letter_tokenize)
        return df

    def _letter_tokenize(self, word):
        x = []
        for i in word:
            x.append(list(i))
        return x

    def convert_to_numbers(self, df):
        return df['headline'].apply(lambda sublist: [[ord(letter) - ord("0") for letter in word] for word in sublist])

    def combine_inner_arrays(self, row):
        return sum(row, [])

    def pad_inner_array(self, df):
        max_len = df['headline'].apply(len).max()
        df['headline'] = df['headline'].apply(lambda x: x + [0] * (max_len - len(x)))
        return df['headline']

    def predict(self, df_numpy):
        model = tf.keras.saving.load_model("stellar_signals/finance_sentiment.keras")
        predictions = np.argmax( model.predict(df_numpy), axis=1 )
        print(predictions)
        return np.mean(predictions)

if __name__ == '__main__':
    analysis = SentimentAnalysis()
    analysis.setup()
    analysis.get_news(ticker='GWW')
    df = pd.DataFrame(analysis.headlines['GWW'], columns=['headline'])
    df = df.drop_duplicates(subset=['headline'])
    df = analysis.preprocess(df)
    mean = analysis.predict(df)
    print(mean)
    # for ticker in secmaster_ticker_list:
        # analysis.get_news(ticker=ticker)
        # df = pd.DataFrame(analysis.headlines[ticker], columns=['headline'])
        # df = df.drop_duplicates(subset=['headline'])
        # df = analysis.preprocess(df)
        # mean = analysis.predict(df)
        # print(ticker, mean)
    
    # analysis.get_news(ticker="TSLA")
    # df = pd.DataFrame(analysis.headlines["TSLA"], columns=['headline'])
    # df = df.drop_duplicates(subset=['headline'])
    # print(list(df['headline'])[:13])
    # df = analysis.preprocess(df)
    # mean = analysis.predict(df)
    # print("TSLA", mean)
