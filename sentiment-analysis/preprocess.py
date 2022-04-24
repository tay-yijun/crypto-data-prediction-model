import re
from typing import List

import nltk.corpus
import pandas as pd
from nltk import WordNetLemmatizer
nltk.data.path.append("/tmp")

nltk.download('words', download_dir="/tmp")

EMOJIS = {':)': 'smile', ':-)': 'smile', ';d': 'wink', ':-E': 'vampire', ':(': 'sad',
          ':-(': 'sad', ':-<': 'sad', ':P': 'raspberry', ':O': 'surprised',
          ':-@': 'shocked', ':@': 'shocked', ':-$': 'confused', ':\\': 'annoyed',
          ':#': 'mute', ':X': 'mute', ':^)': 'smile', ':-&': 'confused', '$_$': 'greedy',
          '@@': 'eyeroll', ':-!': 'confused', ':-D': 'smile', ':-0': 'yell', 'O.o': 'confused',
          '<(-_-)>': 'robot', 'd[-_-]b': 'dj', ":'-)": 'sadsmile', ';)': 'wink',
          ';-)': 'wink', 'O:-)': 'angel', 'O*-)': 'angel', '(:-D': 'gossip', '=^.^=': 'cat'}
STOPWORDS = ['a', 'about', 'above', 'after', 'again', 'ain', 'all', 'am', 'an',
             'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before',
             'being', 'below', 'between', 'both', 'by', 'can', 'd', 'did', 'do',
             'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from',
             'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here',
             'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in',
             'into', 'is', 'it', 'its', 'itself', 'just', 'll', 'm', 'ma',
             'me', 'more', 'most', 'my', 'myself', 'now', 'o', 'of', 'on', 'once',
             'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'own', 're',
             's', 'same', 'she', "shes", 'should', "shouldve", 'so', 'some', 'such',
             't', 'than', 'that', "thatll", 'the', 'their', 'theirs', 'them',
             'themselves', 'then', 'there', 'these', 'they', 'this', 'those',
             'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was',
             'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
             'why', 'will', 'with', 'won', 'y', 'you', "youd", "youll", "youre",
             "youve", 'your', 'yours', 'yourself', 'yourselves']
WORDS = set(nltk.corpus.words.words())


def preprocess_tweet(textdata: str) -> List[str]:
    """
    Apply filters and transformations on each text record
    :param textdata: str
    :return: List[str]
    """
    processedText = []


    # Defining regex patterns.
    urlPattern = r"((http://)[^ ]*|(https://)[^ ]*|( www\.)[^ ]*)"
    userPattern = '@[^\s]+'
    alphaPattern = "[^a-zA-Z0-9]"
    sequencePattern = r"(.)\1\1+"
    seqReplacePattern = r"\1\1"

    tweet = textdata.lower()

    # Replace all URls with 'URL'
    tweet = re.sub(urlPattern, ' ', tweet)
    # Replace all emojis.
    for emoji in EMOJIS.keys():
        tweet = tweet.replace(emoji, "EMOJI" + EMOJIS[emoji])
        # Replace @USERNAME to 'USER'.
    tweet = re.sub(userPattern, ' ', tweet)
    # Replace all non alphabets.
    tweet = re.sub(alphaPattern, " ", tweet)
    # Replace 3 or more consecutive letters by 2 letter.
    tweet = re.sub(sequencePattern, seqReplacePattern, tweet)
    # Replace non-english words
    tweet = " ".join(w for w in nltk.wordpunct_tokenize(tweet) if w.lower() in WORDS)

    tweetwords = ''
    for word in tweet.split():
        # Checking if the word is a stopword.
        if word not in STOPWORDS:
            # Replace non-english words
            if len(word) > 1:
                tweetwords += (word + ' ')
    processedText.append(tweetwords)
    return processedText


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply preprocessing pipeline on input dataframe
    :param df: pd.DataFrame
    :return: pd.DataFrame
    """
    # select necessary column
    df = df[['created_at', 'text']]
    # filter Retweets
    clean = df[~df.text.str.startswith('RT', na=False)]
    # filter giveaway tweets
    clean = clean[~clean.text.str.contains('giveaway')]
    # apply preprocessing on each tweet
    applied_clean = clean.apply(lambda row: preprocess_tweet(row.text), axis='columns', result_type='expand')
    # append the processed_text column with the input df
    out = pd.concat([clean, applied_clean], axis='columns')
    out.columns = ['time', 'text', 'processed_text']
    # filter out empty records
    out = out[out['processed_text'].str.strip().astype(bool)]
    return out

