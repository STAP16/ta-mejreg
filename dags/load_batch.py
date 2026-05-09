from airflow import DAG
from airflow.operators.python import PythonOperator
from calc_batch import calc_batch


with DAG(
    'load_batch',
    description='Пересчет исторических метрик',
    schedule_interval=None
) as dag:

    calc_task = PythonOperator(
      task_id='calc_metrics',
      python_callable=calc_batch,
    )

    calc_task