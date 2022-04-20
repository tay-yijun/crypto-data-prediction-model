import datetime

import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='send_price_data',
    schedule_interval='*/5 * * * *',
    start_date=pendulum.datetime(2021, 4, 21, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    tags=['price_update'],
) as dag:
    make_forecast = BashOperator(
        task_id='send_price_data',
        bash_command='python3 /home/ubuntu/crypto-data-prediction-model/price-forecasting/send_price_data.py',
    )

    complete_task = BashOperator(
        task_id='complete_task',
        bash_command='echo "job done"',
    )

if __name__ == "__main__":
    dag.cli()