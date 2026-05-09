def transform_bronze_to_silver():
	import pandas as pd
	import random
	DIRECTION = ["north", "south"]

	def calc_speed(first, last):
		import numpy as np
		dist = np.sqrt(
			(last["center_x"] - first["center_x"]) ** 2 +
			(last["center_y"] - first["center_y"]) ** 2
		)
		time_diff = (last["timestamp"] - first["timestamp"]).dt.total_seconds()
		time_diff = time_diff.replace(0, np.nan)
		speed_kmh = ((dist/time_diff) * 3.6) * 10
		speed_kmh = np.clip(speed_kmh, 0, 200)
		return round(speed_kmh, 2)


	from clickhouse_connect import get_client
	client = get_client(password="click", username="click", host="clickhouse", port=8123)

	result = client.query("SELECT max(timestamp) FROM silver_detections")
	last_ts = result.result_rows[0][0]

	if pd.isna(last_ts) or last_ts is None:
		df = client.query_df("""SELECT * FROM bronze_detections WHERE confidence > 0.5""")
		print("Данных нету - грузим полностью")
	else: 
		df = client.query_df(
			f"""SELECT * FROM bronze_detections WHERE confidence > 0.5 AND timestamp > '{last_ts}' ORDER BY timestamp ASC """
		)
		print(f"Инкрементальная загрузка с {last_ts}")

	if df.empty:
		print("Df пустой, нечего обрабатывать")
		return

	first_track_point = df.groupby("track_id").first()
	last_track_point = df.groupby("track_id").last()
	speed_km_h = calc_speed(first_track_point, last_track_point)
	df["speed_kmh"] = df["track_id"].map(speed_km_h).fillna(0)
	df["direction"] = DIRECTION[random.randint(0, 1)]

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

	client.insert_df("silver_detections", df[columns_name], column_names=columns_name)
	print("Вставка успешно выполена")