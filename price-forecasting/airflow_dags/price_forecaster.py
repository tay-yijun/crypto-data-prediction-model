import datetime

import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='price_forecaster',
    schedule_interval='*/5 * * * *',
    start_date=pendulum.datetime(2021, 4, 21, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    tags=['machine_learning'],
) as dag:
    make_forecast = BashOperator(
        task_id='make_forecast',
        bash_command='python3 /home/ubuntu/crypto-data-prediction-model/price-forecasting/make_forecast.py',
    )

    complete_task = BashOperator(
        task_id='complete_task',
        bash_command='echo "job done"',
    )

if __name__ == "__main__":
    dag.cli()