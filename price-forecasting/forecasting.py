from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, LongType, StructField
from pyspark.sql.window import Window
from pyspark.sql.functions import col
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation
from fbprophet.diagnostics import performance_metrics
from fbprophet.plot import plot_cross_validation_metric

def TimeSeriesSplit(df_m, splitRatio, sparksession):

    # Splitting data into train and test
    # we maintain the time-order while splitting
    # if split ratio = 0.7 then first 70% of data is train data
    # and remaining 30% of data is test data
    newSchema  = StructType(df_m.schema.fields + \
                [StructField("Row Number", LongType(), False)])
    new_rdd = df_m.rdd.zipWithIndex().map(lambda x: list(x[0]) + [x[1]])
    df_m2 = sparksession.createDataFrame(new_rdd, newSchema)
    total_rows = df_m2.count()
    splitFraction  =int(total_rows*splitRatio)
    df_train = df_m2.where(df_m2["Row Number"] >= 0) \
                   .where(df_m2["Row Number"] <= splitFraction) \
                    .drop("Row Number")
    df_test = df_m2.where(df_m2["Row Number"] > splitFraction) \
                    .drop("Row Number")
    
    return df_train, df_test

    # def CheckStationarity(timeSeriesCol):
    #     # this function works with Pandas dataframe only not with spark dataframes
    #     # this performs Augmented Dickey-Fuller's test
    #
    #     test_result = adfuller(timeSeriesCol.values)
    #     print("ADF Statistic: % f \n" % test_result[0])
    #     print("p - value: % f \n"" % test_result[1]")
    #     print("Critical values are: \n")
    #     print(test_result[4])
    #
    # return df_train, df_test

def Predict(I, df1, df2, timeSeriesCol, predictionCol, joinCol):
    
    # this converts differenced predictions to raw predictions
    dZCol = "DeltaZ" + str(i) 
    f_strCol = "forecast_"+str(i)+"day"
    df = df1.join(df2, [joinCol], how="inner")\
                            .orderBy(asc("Date"))
    df = df.withColumnRenamed(predictionCol, dZCol)
    df = df.withColumn(f_strCol, col(dZCol)+col(timeSeriesCol))
    return df

def main():
    spark = SparkSession. \
        builder. \
        appName("price-forecasting-btc-2014-2021"). \
        getOrCreate()
    btc_usd = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv("BTC-USD.csv")
    btc_usd \
        .orderBy("Date") \
        .show()

    """
    +----------+----------+----------+----------+----------+----------+--------+
    |      Date|      Open|      High|       Low|     Close| Adj Close|  Volume|
    +----------+----------+----------+----------+----------+----------+--------+
    |2014-09-17|465.864014|468.174011|452.421997|457.334015|457.334015|21056800|
    |2014-09-18|456.859985|456.859985|413.104004|424.440002|424.440002|34483200|
    |2014-09-19|424.102997|427.834991|384.532013| 394.79599| 394.79599|37919700|
    |2014-09-20|394.673004| 423.29599|389.882996|408.903992|408.903992|36863600|
    |2014-09-21|408.084991|412.425995|   393.181|398.821014|398.821014|26580100|
    |2014-09-22|399.100006|406.915985|397.130005|402.152008|402.152008|24127600|
    """

    btc_usd \
        .summary("count", "min", "25%", "75%", "max") \
        .show()
    """
    +-------+----------+------------+------------+------------+------------+------------+------------+
    |summary|      Date|        Open|        High|         Low|       Close|   Adj Close|      Volume|
    +-------+----------+------------+------------+------------+------------+------------+------------+
    |  count|      2713|        2713|        2713|        2713|        2713|        2713|        2713|
    |    min|2014-09-17|  176.897003|  211.731003|  171.509995|  178.102997|  178.102997|     5914570|
    |    25%|      null|  606.396973|  609.260986|  604.109985|  606.718994|  606.718994|    79910800|
    |    75%|      null|10452.399414|10762.644531|10202.387695|10462.259766|10462.259766| 24569921549|
    |    max|2022-02-19|67549.734375|   68789.625|  66382.0625|67566.828125|67566.828125|350967941479|
    +-------+----------+------------+------------+------------+------------+------------+------------+
    """

    date_window = Window.partitionBy().orderBy("Date")
    btc_usd_lag = btc_usd.withColumn("PrevDayOpen",
                                     F.lag(col("Open")).over(date_window))
    btc_usd_lag.show()
    """
    +----------+----------+----------+----------+----------+----------+--------+-----------+
    |      Date|      Open|      High|       Low|     Close| Adj Close|  Volume|PrevDayOpen|
    +----------+----------+----------+----------+----------+----------+--------+-----------+
    |2014-09-17|465.864014|468.174011|452.421997|457.334015|457.334015|21056800|       null|
    |2014-09-18|456.859985|456.859985|413.104004|424.440002|424.440002|34483200| 465.864014|
    |2014-09-19|424.102997|427.834991|384.532013| 394.79599| 394.79599|37919700| 456.859985|
    |2014-09-20|394.673004| 423.29599|389.882996|408.903992|408.903992|36863600| 424.102997|
    |2014-09-21|408.084991|412.425995|   393.181|398.821014|398.821014|26580100| 394.673004|
    """

    btc_usd_lag_diff = btc_usd_lag \
                        .withColumn("diff", F.when(F.isnull(col("Open") - col("PrevDayOpen")), 0).otherwise(col("Open") - col("PrevDayOpen")))
    btc_usd_lag_diff.show()

    btc_usd_date_diff = btc_usd_lag_diff \
        .select("Date", "diff") \
        .withColumnRenamed("Date", "ds") \
        .withColumnRenamed("diff", "y")

    train_df, test_df = TimeSeriesSplit(btc_usd_date_diff, 0.7, spark)

    train_df.show()
    # +----------+-------------------+
    # | ds | y |
    # +----------+-------------------+
    # | 2014 - 0
    # 9 - 17 | 0.0 |
    # | 2014 - 0
    # 9 - 18 | -9.004029000000003 |
    # | 2014 - 0
    # 9 - 19 | -32.75698799999998 |
    # | 2014 - 0
    # 9 - 20 | -29.429993000000024 |
    # | 2014 - 0
    # 9 - 21 | 13.41198700000001 |
    # | 2014 - 0
    # 9 - 22 | -8.984984999999995 |

    test_df.show()
    # +----------+-------------------+
    # | ds | y |
    # +----------+-------------------+
    # | 2019 - 11 - 30 | 297.33007799999996 |
    # | 2019 - 12 - 01 | -192.44091800000024 |
    # | 2019 - 12 - 02 | -147.58007799999996 |
    # | 2019 - 12 - 03 | -100.06054700000004 |
    # | 2019 - 12 - 04 | -3.8505859999995664 |
    # | 2019 - 12 - 05 | -66.88330099999985 |

    # TODO: https://databricks.com/blog/2021/04/06/fine-grained-time-series-forecasting-at-scale-with-facebook-prophet-and-apache-spark-updated-for-spark-3.html
    # TODO: https://databricks.com/wp-content/uploads/notebooks/fine-grained-demand-forecasting-spark-3.html

    model = Prophet(
      interval_width=0.95,
      growth='linear',
      daily_seasonality=False,
      weekly_seasonality=True,
      yearly_seasonality=True,
      seasonality_mode='multiplicative'
      )
    model.fit(train_df.toPandas())

    # Make a future facing dataset for the next 30 days to forecast out on
    future = model.make_future_dataframe(periods=30, freq='d')
    forecast = model.predict(future)
    print(forecast.head(30))
    forecast.to_csv("./out/out-sample-30d-forecast.csv", header=True, sep=",")

    # Make forecast on test data
    test_data_with_forecast = model.predict(test_df.toPandas())
    test_data_with_forecast.to_csv("./out/test-data-forecast.csv", header=True, sep=",")


if __name__ == "__main__":
    main()