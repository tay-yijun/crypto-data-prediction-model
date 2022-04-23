
from datetime import timedelta

from common import create_ts_files, TimeSeriesLoader, get_transactions, DAYS_OF_DATA_FOR_TRAINING, HISTORY_STEPS, STEP_SIZE, make_forecast_df
import numpy as np
import tensorflow as tf
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import layers

PICKLE_MODEL = True
MODEL_OUT_PATH = "model"
SAMPLING_RATIO = 0.75


# Source https://towardsdatascience.com/3-steps-to-forecast-time-series-lstm-with-tensorflow-keras-ba88c6f05237
# Another good source https://colab.research.google.com/drive/1wWvtA5RC6-is6J8W86wzK52Knr3N1Xbm
def main():
    df2: pd.DataFrame = get_transactions(lookback_in_days=DAYS_OF_DATA_FOR_TRAINING, sampling_ratio=SAMPLING_RATIO)
    print(f"Dataframe has dimensions {df2.size}")

    val_cutoff_date = df2['date_time'].max() - timedelta(days=2)
    df_val = df2[(df2['date_time'] > val_cutoff_date)]
    df_train = df2[df2['date_time'] <= val_cutoff_date]

    print('Validation dates: {} to {}'.format(df_val['date_time'].min(), df_val['date_time'].max()))
    print('Train dates: {} to {}'.format(df_train['date_time'].min(), df_train['date_time'].max()))

    # Scaled to work with Neural networks.
    price = df_train["price"].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    price_scaled = scaler.fit_transform(price.reshape(-1, 1)).reshape(-1, )

    history_length = HISTORY_STEPS  # The history length in minutes.
    step_size = STEP_SIZE  # The sampling rate of the history. Eg. If step_size = 1, then values from every minute will be in the history.
                    #                                       If step size = 10 then values every 10 minutes will be in the history.
    target_step = 10  # The time step in the future to predict. Eg. If target_step = 0, then predict the next timestep after the end of the history period.
                      #                                             If target_step = 10 then predict 10 timesteps the next timestep (11 minutes after the end of history).

    # The csv creation returns the number of rows and number of features. We need these values below.
    num_timesteps, no_file_created = create_ts_files(price_scaled,
                                    start_index=0,
                                    end_index=None,
                                    history_length=history_length,
                                    step_size=step_size,
                                    target_step=target_step,
                                    num_rows_per_file=128*100,
                                    data_folder='ts_data')

    # I found that the easiest way to do time series with tensorflow is by creating pandas files with the lagged time steps (eg. x{t-1}, x{t-2}...) and
    # the value to predict y = x{t+n}. We tried doing it using TFRecords, but that API is not very intuitive and lacks working examples for time series.
    # The resulting file using these parameters is over 17GB. If history_length is increased, or  step_size is decreased, it could get much bigger.
    # Hard to fit into laptop memory, so need to use other means to load the data from the hard drive.
    ts_folder = 'ts_data'
    filename_format = 'ts_file{}.pkl'
    tss = TimeSeriesLoader(ts_folder, filename_format)

    # Create the Keras model.
    # Use hyperparameter optimization if you have the time.
    ts_inputs = tf.keras.Input(shape=(int(num_timesteps), 1))

    # units=10 -> The cell and hidden states will be of dimension 10.
    #             The number of parameters that need to be trained = 4*units*(units+2)
    x = layers.LSTM(units=10)(ts_inputs)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(1, activation='linear')(x)
    model = tf.keras.Model(inputs=ts_inputs, outputs=outputs)

    model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.01),
                  loss=tf.keras.losses.MeanSquaredError(),
                  metrics=['mse'])

    model.summary()

    # train in batch sizes of 128.
    BATCH_SIZE = 128
    NUM_EPOCHS = 1
    NUM_CHUNKS = tss.num_chunks()

    for epoch in range(NUM_EPOCHS):
        print('epoch #{}'.format(epoch))
        for i in range(NUM_CHUNKS):
            X, y = tss.get_chunk(i)

            # model.fit does train the model incrementally. ie. Can call multiple times in batches.
            # https://github.com/keras-team/keras/issues/4446
            model.fit(x=X, y=y, batch_size=BATCH_SIZE)

        # shuffle the chunks so they're not in the same order next time around.
        tss.shuffle_chunks()


    # evaluate the model on the validation set.
    #
    # Create the validation CSV like we did before with the training.
    price_val = df_val['price'].values
    price_val_scaled = scaler.transform(price_val.reshape(-1, 1)).reshape(-1, )

    history_length = HISTORY_STEPS  # The history length in minutes.
    step_size = 10  # The sampling rate of the history. Eg. If step_size = 1, then values from every minute will be in the history.
    #                                       If step size = 10 then values every 10 minutes will be in the history.
    target_step = 10  # The time step in the future to predict. Eg. If target_step = 0, then predict the next timestep after the end of the history period.
    #                                             If target_step = 10 then predict 10 timesteps the next timestep (11 minutes after the end of history).

    # The csv creation returns the number of rows and number of features. We need these values below.
    num_timesteps = create_ts_files(price_val_scaled,
                                    start_index=0,
                                    end_index=None,
                                    history_length=history_length,
                                    step_size=step_size,
                                    target_step=target_step,
                                    num_rows_per_file=128 * 100,
                                    data_folder='ts_val_data')

    # If we assume that the validation dataset can fit into memory we can do this.
    # If we assume that the validation dataset can fit into memory we can do this.
    df_val_ts: pd.DataFrame = pd.read_pickle('ts_val_data/ts_file0.pkl')

    print("dataset")
    print(df_val_ts.head())
    print(df_val_ts.size)

    y_pred = make_forecast_df(df=df_val_ts, model=model, scaler=scaler)

    y_act = df_val_ts['y'].values
    y_act = scaler.inverse_transform(y_act.reshape(-1, 1)).reshape(-1, )

    print('validation mean squared error: {}'.format(mean_squared_error(y_act, y_pred)))

    # baseline
    y_pred_baseline = df_val_ts['x_lag11'].values
    y_pred_baseline = scaler.inverse_transform(y_pred_baseline.reshape(-1, 1)).reshape(-1, )
    print('validation baseline mean squared error: {}'.format(mean_squared_error(y_act, y_pred_baseline)))

    output_df = pd.DataFrame(data=np.column_stack((y_pred_baseline, y_pred, y_act)), columns=["baseline", "lstm", "actual"])
    output_df.to_csv(path_or_buf="out/predictions-lstm.csv", header=True)

    if PICKLE_MODEL:
        print(f"Write model to {MODEL_OUT_PATH}")
        model.save(filepath=MODEL_OUT_PATH, overwrite=True)


if __name__ == "__main__":
    main()
