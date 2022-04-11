import datetime

import pandas as pd
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from common import create_ts_files, TimeSeriesLoader, get_transactions, DAYS_OF_DATA_FOR_FORECASTING, HISTORY_STEPS, STEP_SIZE, make_forecast_df, get_postgres_connection

def main():
    print("Begin")
    df: pd.DataFrame = get_transactions(lookback_in_days=DAYS_OF_DATA_FOR_FORECASTING, sampling_ratio=1.0)
    print(df.head())
    print(df.size)
    print(df["date_time"].min())
    print(df["date_time"].max())

    model = keras.models.load_model("model")
    print(model)

    price = df['price'].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    price_scaled = scaler.fit_transform(price.reshape(-1, 1)).reshape(-1, )

    history_length = HISTORY_STEPS  # The history length in minutes.
    step_size = 10  # The sampling rate of the history. Eg. If step_size = 1, then values from every minute will be in the history.
    #                                       If step size = 10 then values every 10 minutes will be in the history.
    target_step = 10  # The time step in the future to predict. Eg. If target_step = 0, then predict the next timestep after the end of the history period.
    #                                             If target_step = 10 then predict 10 timesteps the next timestep (11 minutes after the end of history).

    num_timesteps, last_file_no = create_ts_files(price_scaled,
                                    start_index=0,
                                    end_index=None,
                                    history_length=history_length,
                                    step_size=step_size,
                                    target_step=target_step,
                                    num_rows_per_file=256 * 100,
                                    data_folder='ts_forecasting_data')
    print(f"Last file number {last_file_no}")

    data_df: pd.DataFrame = pd.read_pickle(f"ts_forecasting_data/ts_file{last_file_no-1}.pkl")
    y_pred = make_forecast_df(model=model, df=data_df, scaler=scaler)
    print(y_pred)
    forecast_price= y_pred[-1].item()

    prediction_time = df["date_time"].max().to_pydatetime() + datetime.timedelta(minutes=5)

    print(f"Write prediction time {prediction_time} and bitcoin price {forecast_price} to postgres")
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO public.price_forecasts (forecast_future_time, forecast_btc_price) VALUES (%s, %s)", (prediction_time, forecast_price))
    conn.commit()
    cursor.close()
    conn.close()



if __name__ == "__main__":
    main()