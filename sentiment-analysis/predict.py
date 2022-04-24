import json
import os
from typing import Any, Dict

import pandas as pd
import joblib

from preprocess import preprocess
from utils import save_result

from boto.s3.key import Key
from boto.s3.connection import S3Connection
from flask import Flask
from flask import request
from flask import json
ACCESS_KEY_ID = ''
ACCESS_KEY_SECRET= ''


BUCKET_NAME = 'nus-bead-project-sentiment-1'
MODEL_FILE_NAME = 'Sentiment-SVC.pkl'
VECTORISER_NAME = 'vectoriser-ngram-(1,1).pkl'
MODEL_LOCAL_PATH = '/tmp/' + MODEL_FILE_NAME
VECTORISER_LOCAL_PATH = '/tmp/' + VECTORISER_NAME

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    payload = json.loads(request.get_data().decode('utf-8'))
    prediction = predict(payload['data'])
    return prediction


def load_from_s3(key_name, local_path_name):
    if not os.path.exists(local_path_name):
        conn = S3Connection(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_KEY_SECRET)
        bucket = conn.get_bucket(BUCKET_NAME)
        key_obj = Key(bucket)
        key_obj.key = key_name
        contents = key_obj.get_contents_to_filename(local_path_name)
    return joblib.load(local_path_name)


def predict(payload: Dict[str, Any]) -> pd.DataFrame:
    """
    Prediction pipeline for a given json input
    :param payload:  JSON
    :return: pd.DataFrame
    """
    # loading the json
    data = pd.json_normalize(payload)
    vectoriser = load_from_s3(VECTORISER_NAME, VECTORISER_LOCAL_PATH)
    model = load_from_s3(MODEL_FILE_NAME, MODEL_LOCAL_PATH)
    cleaned = preprocess(data)
    tweets = list(cleaned.processed_text)

    # predict the sentiment
    textdata = vectoriser.transform(tweets)
    sentiment = model.predict(textdata)

    # make a list of text with sentiment
    out = []
    for text, pred in zip(tweets, sentiment):
        out.append((text, pred))
    # convert the list into a Pandas DF
    df = pd.DataFrame(out, columns = ['processed_text','sentiment'])
    df = df.replace([0,1], ["Negative","Positive"])

    # merge the result with input df
    cleaned.reset_index(drop=True)
    df.reset_index(drop=True)
    res = pd.merge(cleaned, df, left_index=True, right_index=True, on=['processed_text'])
    res.drop('processed_text', axis=1, inplace=True)
    content = res.to_json(orient='records')
    parsed = json.loads(content)
    result = {}
    result['data']  = parsed
    return result

if __name__ == '__main__':
    with open('./data/posts.json', 'r', encoding='utf-8') as content:
        data = json.load(content)
    res = predict(data)
    parsed = json.loads(res)
    result = {}
    result['result']  = parsed
    print(result)
    # save_result(res, 'out')
