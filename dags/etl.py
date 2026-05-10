from datetime import datetime

from airflow import DAG
from transform_bronze_to_silver import transform_bronze_to_silver
from build_mart import build_mart
from build_v_heavy_truck_patterns import build_v_heavy_truck_patterns
from build_vehicle_structure import build_vehicle_structure
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

	build_heavy_truck = PythonOperator(
		task_id='build_heavy_truck',
		python_callable=build_v_heavy_truck_patterns,
	)

	build_vehicle_struc = PythonOperator(
		task_id='build_structure',
		python_callable=build_vehicle_structure,
	)

	transform_b_to_s >> [build_realtime, build_heavy_truck, build_vehicle_struc]