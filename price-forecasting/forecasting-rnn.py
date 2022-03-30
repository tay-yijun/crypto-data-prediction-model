import os
import datetime
from typing import List


import numpy as np
import tensorflow as tf
import pandas as pd

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

def make_dataset(self, data):
  data = np.array(data, dtype=np.float32)
  ds = tf.keras.preprocessing.timeseries_dataset_from_array(
      data=data,
      targets=None,
      sequence_length=self.total_window_size,
      sequence_stride=1,
      shuffle=True,
      batch_size=32,)

  ds = ds.map(self.split_window)

  return ds

# Add this method into the WindowGenerator class
WindowGenerator.make_dataset = make_dataset

@property
def train(self):
  return self.make_dataset(self.train_df)

@property
def val(self):
  return self.make_dataset(self.val_df)

@property
def test(self):
  return self.make_dataset(self.test_df)

@property
def example(self):
  """Get and cache an example batch of `inputs, labels` for plotting."""
  result = getattr(self, '_example', None)
  if result is None:
    # No example batch was found, so get one from the `.train` dataset
    result = next(iter(self.train))
    # And cache it for next time
    self._example = result
  return result

# Add this method into the WindowGenerator class
WindowGenerator.train = train
WindowGenerator.val = val
WindowGenerator.test = test
WindowGenerator.example = example

MAX_EPOCHS = 20

def compile_and_fit(model, window, patience=2):
  early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                    patience=patience,
                                                    mode='min')

  model.compile(loss=tf.losses.MeanSquaredError(),
                optimizer=tf.optimizers.Adam(),
                metrics=[tf.metrics.MeanAbsoluteError()])

  history = model.fit(window.train, epochs=MAX_EPOCHS,
                      validation_data=window.val,
                      callbacks=[early_stopping])
  return history

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

    print(w2.train.element_spec)

    for example_inputs, example_labels in w2.train.take(1):
        print(f'Inputs shape (batch, time, features): {example_inputs.shape}')
        print(f'Labels shape (batch, time, features): {example_labels.shape}')
        # (TensorSpec(shape=(None, 6, 6), dtype=tf.float32, name=None),
        #  TensorSpec(shape=(None, 1, 1), dtype=tf.float32, name=None))
        # Inputs
        # shape(batch, time, features): (32, 6, 6)
        # Labels
        # shape(batch, time, features): (32, 1, 1)

    class Baseline(tf.keras.Model):
        def __init__(self, label_index=None):
            super().__init__()
            self.label_index = label_index

        def call(self, inputs):
            if self.label_index is None:
                return inputs
            result = inputs[:, :, self.label_index]
            return result[:, :, tf.newaxis]

    print("*** Single Step Window Baseline")
    single_step_window = WindowGenerator(
        input_width=1, label_width=1, shift=1,
        train_df=train_df, val_df=val_df, test_df=test_df,
        label_columns=["Open"])
    print(single_step_window)

    baseline = Baseline(label_index=column_indices["Open"])
    baseline.compile(loss=tf.losses.MeanSquaredError(),
                     metrics=[tf.metrics.MeanAbsoluteError()])

    val_performance = {}
    performance = {}
    val_performance['Baseline'] = baseline.evaluate(single_step_window.val)
    performance['Baseline'] = baseline.evaluate(single_step_window.test, verbose=0)

    print("*** Wide window")
    wide_window = WindowGenerator(
        input_width=24, label_width=24, shift=1,
        train_df=train_df, val_df=val_df, test_df=test_df,
        label_columns=['Open'])

    print(wide_window)
    print('Input shape:', wide_window.example[0].shape)
    print('Output shape:', baseline(wide_window.example[0]).shape)

    print("*** Linear model")
    linear = tf.keras.Sequential([
        tf.keras.layers.Dense(units=1)
    ])
    print('Input shape:', single_step_window.example[0].shape)
    print('Output shape:', linear(single_step_window.example[0]).shape)
    history = compile_and_fit(linear, single_step_window)

    val_performance['Linear'] = linear.evaluate(single_step_window.val)
    performance['Linear'] = linear.evaluate(single_step_window.test, verbose=0)


    print("*** Dense model")
    dense = tf.keras.Sequential([
        tf.keras.layers.Dense(units=64, activation='relu'),
        tf.keras.layers.Dense(units=64, activation='relu'),
        tf.keras.layers.Dense(units=1)
    ])

    history = compile_and_fit(dense, single_step_window)

    val_performance['Dense'] = dense.evaluate(single_step_window.val)
    performance['Dense'] = dense.evaluate(single_step_window.test, verbose=0)

    print("*** Multi step dense")
    CONV_WIDTH = 3
    conv_window = WindowGenerator(
        input_width=CONV_WIDTH,label_width=1,shift=1,
        train_df=train_df, val_df=val_df, test_df=test_df,
        label_columns=['Open'])

    print(conv_window)

    multi_step_dense = tf.keras.Sequential([
        # Shape: (time, features) => (time*features)
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(units=32, activation='relu'),
        tf.keras.layers.Dense(units=32, activation='relu'),
        tf.keras.layers.Dense(units=1),
        # Add back the time dimension.
        # Shape: (outputs) => (1, outputs)
        tf.keras.layers.Reshape([1, -1]),
    ])
    print('Input shape:', conv_window.example[0].shape)
    print('Output shape:', multi_step_dense(conv_window.example[0]).shape)

    history = compile_and_fit(multi_step_dense, conv_window)

    val_performance['Multi step dense'] = multi_step_dense.evaluate(conv_window.val)
    performance['Multi step dense'] = multi_step_dense.evaluate(conv_window.test, verbose=0)

    print("Convolution neural network")
    conv_model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(filters=32,
                               kernel_size=(CONV_WIDTH,),
                               activation='relu'),
        tf.keras.layers.Dense(units=32, activation='relu'),
        tf.keras.layers.Dense(units=1),
    ])
    print("Conv model on `conv_window`")
    print('Input shape:', conv_window.example[0].shape)
    print('Output shape:', conv_model(conv_window.example[0]).shape)

    history = compile_and_fit(conv_model, conv_window)

    val_performance['Conv'] = conv_model.evaluate(conv_window.val)
    performance['Conv'] = conv_model.evaluate(conv_window.test, verbose=0)

    print("*** Wide window convolution neural network")
    print("Wide window")
    print('Input shape:', wide_window.example[0].shape)
    print('Labels shape:', wide_window.example[1].shape)
    print('Output shape:', conv_model(wide_window.example[0]).shape)

    LABEL_WIDTH = 24
    INPUT_WIDTH = LABEL_WIDTH + (CONV_WIDTH - 1)
    wide_conv_window = WindowGenerator(
        input_width=INPUT_WIDTH,label_width=LABEL_WIDTH,shift=1,
        train_df=train_df, val_df=val_df, test_df=test_df,
        label_columns=["Open"])

    print(wide_conv_window)
    print("*** Wide conv window")
    print('Input shape:', wide_conv_window.example[0].shape)
    print('Labels shape:', wide_conv_window.example[1].shape)
    print('Output shape:', conv_model(wide_conv_window.example[0]).shape)


    print("***L STM Recurrent neural network")
    lstm_model = tf.keras.models.Sequential([
        # Shape [batch, time, features] => [batch, time, lstm_units]
        tf.keras.layers.LSTM(32, return_sequences=True),
        # Shape => [batch, time, features]
        tf.keras.layers.Dense(units=1)
    ])

    print('Input shape:', wide_window.example[0].shape)
    print('Output shape:', lstm_model(wide_window.example[0]).shape)

    history = compile_and_fit(lstm_model, wide_window)
    val_performance['LSTM'] = lstm_model.evaluate(wide_window.val)
    performance['LSTM'] = lstm_model.evaluate(wide_window.test, verbose=0)


if __name__ == "__main__":
    main()