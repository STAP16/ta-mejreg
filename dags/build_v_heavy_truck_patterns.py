def build_v_heavy_truck_patterns():
	from clickhouse_connect import get_client
	import pandas as pd
	client = get_client(password="click", username="click", host="clickhouse", port=8123)
	max_hour = client.query("""SELECT maxOrNull(hour) FROM v_heavy_truck_patterns""").result_columns[0][0]


	if max_hour is not None:
		client.command(f"ALTER TABLE v_heavy_truck_patterns DELETE WHERE hour >= '{max_hour}'")
		sql = f"""
		INSERT INTO v_heavy_truck_patterns (
			hour,
			camera_id,
			direction,
			heavy_count,
			is_peak,
			alert_flag 
		)
		SELECT 
			toStartOfHour(timestamp) as hour,
			camera_id,
			direction,
			uniqIf(track_id, object_type = 'truck' OR object_type = 'bus') as heavy_count,
			if(heavy_count > 15, 1, 0) as is_peak,
			if(heavy_count > 25, 1, 0) as alert_flag
		FROM silver_detections
		WHERE toStartOfHour(timestamp) > '{max_hour}'
		GROUP BY toStartOfHour(timestamp), camera_id, direction
		"""
	else: 
		print("No data, loading all")
		sql = f"""
		INSERT INTO v_heavy_truck_patterns (
			hour,
			camera_id,
			direction,
			heavy_count,
			is_peak,
			alert_flag 
		)
		SELECT 
			toStartOfHour(timestamp) as hour,
			camera_id,
			direction,
			uniqIf(track_id, object_type = 'truck' OR object_type = 'bus') as heavy_count,
			if(heavy_count > 15, 1, 0) as is_peak,
			if(heavy_count > 25, 1, 0) as alert_flag
		FROM silver_detections
		GROUP BY toStartOfHour(timestamp), camera_id, direction
		"""

	client.command(sql)
