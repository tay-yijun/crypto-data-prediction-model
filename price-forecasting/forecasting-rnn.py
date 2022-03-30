import os
import datetime
from typing import List

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf

# Refer to https://colab.research.google.com/github/tensorflow/docs/blob/master/site/en/tutorials/structured_data/time_series.ipynb#scrollTo=Kem30j8QHxyW

class WindowGenerator():
  def __init__(self, input_width: int, label_width: int, shift: int,
               train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame,
               label_columns: List[str]=None):
    # Store the raw data.
    self.train_df = train_df
    self.val_df = val_df
    self.test_df = test_df

    # Work out the label column indices.
    self.label_columns = label_columns
    if label_columns is not None:
      self.label_columns_indices = {name: i for i, name in
                                    enumerate(label_columns)}
    self.column_indices = {name: i for i, name in
                           enumerate(train_df.columns)}

    # Work out the window parameters.
    self.input_width = input_width
    self.label_width = label_width
    self.shift = shift

    self.total_window_size = input_width + shift

    self.input_slice = slice(0, input_width)
    self.input_indices = np.arange(self.total_window_size)[self.input_slice]

    self.label_start = self.total_window_size - self.label_width
    self.labels_slice = slice(self.label_start, None)
    self.label_indices = np.arange(self.total_window_size)[self.labels_slice]

  def __str__(self):
    return '\n'.join([
        f'Total window size: {self.total_window_size}',
        f'Input indices: {self.input_indices}',
        f'Label indices: {self.label_indices}',
        f'Label column name(s): {self.label_columns}'])


def split_window(self, features):
  inputs = features[:, self.input_slice, :]
  labels = features[:, self.labels_slice, :]
  if self.label_columns is not None:
    labels = tf.stack(
        [labels[:, :, self.column_indices[name]] for name in self.label_columns],
        axis=-1)

  # Slicing doesn't preserve static shape information, so set the shapes
  # manually. This way the `tf.data.Datasets` are easier to inspect.
  inputs.set_shape([None, self.input_width, None])
  labels.set_shape([None, self.label_width, None])

  return inputs, labels

# Add this method into the WindowGenerator class
WindowGenerator.split_window = split_window



def main():
    btc_df: pd.DataFrame = pd.read_csv(filepath_or_buffer="./BTC-USD.csv", delimiter=",", header="infer")
    print(btc_df.head())
    #            Date        Open        High  ...       Close   Adj Close    Volume
    # 0  2014-09-17  465.864014  468.174011  ...  457.334015  457.334015  21056800
    # 1  2014-09-18  456.859985  456.859985  ...  424.440002  424.440002  34483200
    # 2  2014-09-19  424.102997  427.834991  ...  394.795990  394.795990  37919700
    # 3  2014-09-20  394.673004  423.295990  ...  408.903992  408.903992  36863600
    # 4  2014-09-21  408.084991  412.425995  ...  398.821014  398.821014  26580100

    print(btc_df.columns)
    # Index(['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'], dtype='object')

    print(btc_df.describe())
    #                    Open          High  ...     Adj Close        Volume
    # count   2713.000000   2713.000000  ...   2713.000000  2.713000e+03
    # mean   11311.041069  11614.292482  ...  11323.914637  1.470462e+10
    # std    16106.428891  16537.390649  ...  16110.365010  2.001627e+10
    # min      176.897003    211.731003  ...    178.102997  5.914570e+06
    # 25%      606.396973    609.260986  ...    606.718994  7.991080e+07
    # 50%     6301.569824   6434.617676  ...   6317.609863  5.098183e+09
    # 75%    10452.399414  10762.644531  ...  10462.259766  2.456992e+10
    # max    67549.734375  68789.625000  ...  67566.828125  3.509679e+11

    btc_open_df:pd.DataFrame = btc_df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
    print(btc_open_df)
    #               Open          High  ...     Adj Close       Volume
    # 0       465.864014    468.174011  ...    457.334015     21056800
    # 1       456.859985    456.859985  ...    424.440002     34483200
    # 2       424.102997    427.834991  ...    394.795990     37919700
    # 3       394.673004    423.295990  ...    408.903992     36863600
    # 4       408.084991    412.425995  ...    398.821014     26580100
    # ...            ...           ...  ...           ...          ...
    # 2708  42586.464844  44667.218750  ...  44575.203125  22721659051
    # 2709  44578.277344  44578.277344  ...  43961.859375  19792547657
    # 2710  43937.070313  44132.972656  ...  40538.011719  26246662813
    # 2711  40552.132813  40929.152344  ...  40030.976563  23310007704
    # 2712  40022.132813  40246.027344  ...  40126.429688  22263900160

    column_indices: dict = {name: i for i, name in enumerate(btc_open_df.columns)}
    n: int = len(btc_open_df)
    train_df: pd.DataFrame = btc_open_df[0:int(n * 0.7)]
    val_df: pd.DataFrame = btc_open_df[int(n * 0.7):int(n * 0.9)]
    test_df: pd.DataFrame = btc_open_df[int(n * 0.9):]

    print(len(train_df)) # 1899
    print(len(val_df)) # 542
    print(len(test_df)) # 272

    w1 = WindowGenerator(input_width=24, label_width=1, shift=24,
                         train_df=train_df, val_df=val_df, test_df=test_df,
                         label_columns=["Open"])
    print(w1)
    # Total window size: 48
    # Input indices: [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23]
    # Label indices: [47]
    # Label column name(s): ['Open']

    w2 = WindowGenerator(input_width=6, label_width=1, shift=1,
                         train_df=train_df, val_df=val_df, test_df=test_df,
                         label_columns=["Open"])
    print(w2)
    # Total window size: 7
    # Input indices: [0 1 2 3 4 5]
    # Label indices: [6]
    # Label column name(s): ['Open']

    # Stack three slices, the length of the total window.
    example_window = tf.stack([np.asarray(train_df[:w2.total_window_size]).astype(np.float32),
                               np.asarray(train_df[100:100 + w2.total_window_size]).astype(np.float32),
                               np.asarray(train_df[200:200 + w2.total_window_size]).astype(np.float32)])
    print(example_window)


if __name__ == "__main__":
    main()