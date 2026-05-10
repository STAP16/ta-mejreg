from datetime import datetime

from airflow import DAG
from make_predict import make_predict
from airflow.operators.python import PythonOperator


with DAG(
    'make_predict',
    description='Предсказания в таблицу predictions',
    schedule_interval='*/30 * * * *',
    catchup=False,
		start_date=datetime(2023, 1, 1),
    max_active_runs=1
) as dag:

	make = PythonOperator(
		task_id='make_predict_30min',
		python_callable=make_predict,
	)

	make