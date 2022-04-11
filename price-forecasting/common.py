from time import time
import os
import math

import numpy as np
import pandas as pd
from pymongo import MongoClient

MONGO_USER = "iadd"
MONGO_PASSWORD = "ilovecrypto%21%40%23"
MONGO_HOST = "crypto-data.ynykn.mongodb.net"

DAYS_OF_DATA_FOR_TRAINING = 10
DAYS_OF_DATA_FOR_FORECASTING = 1
HISTORY_STEPS = 2*24*60
STEP_SIZE = 10

def create_ts_files(dataset,
                    start_index,
                    end_index,
                    history_length,
                    step_size,
                    target_step,
                    num_rows_per_file,
                    data_folder):
    assert step_size > 0
    assert start_index >= 0

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    time_lags = sorted(range(target_step + 1, target_step + history_length + 1, step_size), reverse=True)
    col_names = [f'x_lag{i}' for i in time_lags] + ['y']
    start_index = start_index + history_length
    if end_index is None:
        end_index = len(dataset) - target_step

    rng = range(start_index, end_index)
    num_rows = len(rng)
    num_files = math.ceil(num_rows / num_rows_per_file)

    # for each file.
    print(f'Creating {num_files} files.')
    for i in range(num_files):
        filename = f'{data_folder}/ts_file{i}.pkl'

        # get the start and end indices.
        ind0 = i * num_rows_per_file
        ind1 = min(ind0 + num_rows_per_file, end_index)
        data_list = []

        # j in the current timestep. Will need j-n to j-1 for the history. And j + target_step for the target.
        for j in range(ind0, ind1):
            indices = range(j - 1, j - history_length - 1, -step_size)
            data = dataset[sorted(indices) + [j + target_step]]

            # append data to the list.
            data_list.append(data)

        df_ts = pd.DataFrame(data=data_list, columns=col_names)
        print(f'Pickling {filename}')
        df_ts.to_pickle(filename)

    return len(col_names) - 1, num_files


class TimeSeriesLoader:
    def __init__(self, ts_folder, filename_format):
        self.ts_folder = ts_folder
        self.filename_format = filename_format

        # find the number of files.
        i = 0
        file_found = True
        while file_found:
            filename = self.ts_folder + '/' + filename_format.format(i)
            file_found = os.path.exists(filename)
            if file_found:
                i += 1

        self.num_files = i
        self.files_indices = np.arange(self.num_files)
        self.shuffle_chunks()

    def num_chunks(self):
        return self.num_files

    def get_chunk(self, idx):
        assert (idx >= 0) and (idx < self.num_files)

        ind = self.files_indices[idx]
        filename = self.ts_folder + '/' + self.filename_format.format(ind)
        df_ts = pd.read_pickle(filename)
        num_records = len(df_ts.index)

        features = df_ts.drop('y', axis=1).values
        target = df_ts['y'].values

        # reshape for input into LSTM. Batch major format.
        features_batchmajor = np.array(features).reshape(num_records, -1, 1)
        return features_batchmajor, target

    # this shuffles the order the chunks will be outputted from get_chunk.
    def shuffle_chunks(self):
        np.random.shuffle(self.files_indices)

def get_mongo_client():
    return MongoClient(f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}")

def get_transactions(lookback_in_days: int, sampling_ratio: float) -> pd.DataFrame:
    client = get_mongo_client()
    db = client["golangAPI"]
    transactions = db["transactions"]


    val = list(transactions.find().sort("time", -1).limit(1))
    print(val)

    # Get last X days of data
    lookback_time = (time() - (lookback_in_days * 24 * 3600)) * 1000
    print(f"earliest time lookback_time: {lookback_time}")
    training_data = list(transactions.find({"time": {"$gte": lookback_time}}))
    print(len(training_data))
    print(training_data[:10])


    df = pd.DataFrame.from_dict(training_data)
    print(df.head())
    df1 = df.drop(["_id", "id"], axis = 1)
    df1["date_time"] = (pd.to_datetime(df1["time"], unit='ms'))
    df2: pd.DataFrame = df1[["date_time", "price", "qty", "quoteqty"]].sample(frac=sampling_ratio).sort_values(by="date_time", ascending=True)
    print(df2.columns)
    print(df2.describe())
    print(df2.head(100))
    print(df2["date_time"].min())
    print(df2["date_time"].max())

    return df2

def make_forecast_df(model, data_file: str) -> pd.DataFrame:
    pass
