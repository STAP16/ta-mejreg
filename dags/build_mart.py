def build_mart():
	import pandas as pd
	import random
	DIRECTION = ["north", "south"]

	from clickhouse_connect import get_client
	client = get_client(password="click", username="click", host="clickhouse", port=8123)

	result = client.query("SELECT maxOrNull(minute) FROM v_current_load")
	last_minute = result.result_rows[0][0]

	if last_minute is None:
		#Витрина пустая - грузим всё.
		sql = """
			INSERT INTO v_current_load (minute, camera_id, direction, vehicle_count, avg_speed, density)
			SELECT
				toStartOfMinute(timestamp) as minute,
				camera_id,
				direction,
				uniqExact(track_id) as vehicle_count,
				avg(speed_kmh) as avg_speed,
				uniqExact(track_id) / 0.5 as density
			FROM silver_detections
			GROUP BY toStartOfMinute(timestamp), camera_id, direction
		"""
		print("Витрина пустая - грузим всё.")
	else: 
		sql = f"""
			INSERT INTO v_current_load (minute, camera_id, direction, vehicle_count, avg_speed, density)
			SELECT
				toStartOfMinute(timestamp) as minute,
				camera_id,
				direction,
				uniqExact(track_id) as vehicle_count,
				avg(speed_kmh) as avg_speed,
				uniqExact(track_id) / 0.5 as density
			FROM silver_detections
			WHERE timestamp > '{last_minute}'
			GROUP BY toStartOfMinute(timestamp), camera_id, direction
		"""
		print(f"Инкремент с {last_minute}")
	client.command(sql)
	result = client.query("SELECT count() FROM v_current_load")
	print(f"В витрине {result.result_rows[0][0]} строк")