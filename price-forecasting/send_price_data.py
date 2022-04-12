import pandas as pd

from common import get_transactions, get_postgres_connection

def one_time_load():
    df: pd.DataFrame = get_transactions(lookback_in_days=30, sampling_ratio=0.01)
    print(df.describe())
    print(df.size)
    df2: pd.DataFrame = df[["date_time", "price"]]

    conn = get_postgres_connection()
    cursor = conn.cursor()

    for ind in df2.index:
        print(f"row {ind} of {df2.size}")
        date_time = df2["date_time"][ind].to_pydatetime()
        price = df2["price"][ind]
        print(price)
        cursor.execute("INSERT INTO public.bitcoin_price (event_time, btc_usd_price) VALUES (%s, %s)",
                       (date_time, price))
        conn.commit()

    cursor.close()
    conn.close()

def main():
    print("BEGIN")
    df: pd.DataFrame = get_transactions(0.10, sampling_ratio=1.0)
    print(df.describe())
    print(df.tail(5))

    last_row_date_time = df.tail(1)["date_time"].item().to_pydatetime()
    last_row_price = df.tail(1)["price"].item()
    print(last_row_date_time, last_row_price)

    print(f"Write time {last_row_date_time} and price {last_row_price} to postgres")
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO public.bitcoin_price (event_time, btc_usd_price) VALUES (%s, %s)", (last_row_date_time, last_row_price))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
    # one_time_load()