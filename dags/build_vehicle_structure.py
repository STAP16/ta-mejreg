def build_vehicle_structure():
	from clickhouse_connect import get_client

	client = get_client(password="click", username="click", host="clickhouse", port=8123)
	max_minute = client.query("""SELECT maxOrNull(minute) FROM v_vehicle_structure""").result_columns[0][0]

	if max_minute is not None:
			client.command(
				f"ALTER TABLE v_vehicle_structure DELETE WHERE minute >= '{max_minute}'"
			)

			where_clause = f"""
				WHERE toStartOfMinute(timestamp) > '{max_minute}'
			"""
	else:
		print("No data, loading all")
		where_clause = ""

	sql = f"""
	INSERT INTO v_vehicle_structure
	(
		minute,
		camera_id,
		vehicle_type,
		count,
		share_pct
	)
	SELECT
		toStartOfMinute(timestamp) as minute,
		camera_id,
		object_type as vehicle_type,
		count(*) as count,
		0 as share_pct

	FROM silver_detections

	{where_clause}

	GROUP BY
		toStartOfMinute(timestamp),
		camera_id,
		vehicle_type
	"""

	client.command(sql)