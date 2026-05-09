from datetime import datetime

from airflow import DAG
from transform_bronze_to_silver import transform_bronze_to_silver
from build_mart import build_mart
from airflow.operators.python import PythonOperator


with DAG(
    'etl',
    description='Процесс записи потоковых данных в витрину',
    schedule_interval='* * * * *',
    catchup=False,
		start_date=datetime(2023, 1, 1),
    max_active_runs=1
) as dag:

	transform_b_to_s = PythonOperator(
		task_id='transform-and-clear',
		python_callable=transform_bronze_to_silver,
	)

	build_realtime = PythonOperator(
		task_id='build_current_load',
		python_callable=build_mart,
	)

	transform_b_to_s >> build_realtime