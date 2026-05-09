def calc_batch():
	import pandas as pd
	import os
	from clickhouse_connect import get_client
	CAMERA_ID = "1"

	client = get_client(password="click", username="click", host="clickhouse", port=8123)
	dag_dir = os.path.dirname(os.path.abspath(__file__))
	csv_path = os.path.join(dag_dir, 'full_tracking_data.csv')

	df = pd.read_csv(csv_path)
	# video_id,title,path,recording_at,recording_end,track_id,tracker_id,start_time,end_time,object_type,width,length,detection_time,x_cord_m,y_cord_m,total_kms,speed_km_h,direction
	df["speed_kmh"] = df["speed_km_h"]
	df["camera_id"] = CAMERA_ID
	df["timestamp"] = df["detection_time"]
	df["center_x"] = df["x_cord_m"]
	df["center_y"] = df["y_cord_m"]

	columns_name = [
		'timestamp',
		'camera_id',
		'track_id',
		'object_type',
		'center_x',
		'center_y',
		'speed_kmh',
		'direction'
	]

	df = df.dropna()
	client.insert_df("silver_detections", column_names=columns_name, df=df[columns_name])

	print("Пересчет исторических метрик выполнен успешно!")
	print(f"Пересчитано: {len(df)} записей")