CREATE TABLE IF NOT EXISTS v_current_load (
	minute DateTime,
	camera_id String,
	direction String,
	vehicle_count UInt32,
	avg_speed Float32,
	density Float32
)
ENGINE = MergeTree()
ORDER BY (camera_id, minute, direction)
PARTITION BY toYYYYMMDD(minute)

CREATE TABLE IF NOT EXISTS v_forecast_30_60_120 (
	camera_id String,
	direction String,
	horizon_min UInt16,
	predicted_load Float32,
	predicted_speed Float32,
	model_version String,
	created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (camera_id, created_at, horizon_min)
PARTITION BY toYYYYMMDD(created_at)

CREATE TABLE IF NOT EXISTS v_heavy_truck_patterns (
	hour DateTime,
	camera_id String,
	direction String,
	heavy_count UInt32,
	is_peak UInt8,
	alert_flag UInt8
)
ENGINE = MergeTree()
ORDER BY (camera_id, hour, direction)
PARTITION BY toYYYYMMDD(hour)

CREATE TABLE IF NOT EXISTS v_vehicle_structure (
	minute DateTime,
	camera_id String,
	vehicle_type String,
	count UInt32,
	share_pct Float32
)
ENGINE = MergeTree()
ORDER BY (camera_id, minute, vehicle_type)
PARTITION BY toYYYYMMDD(minute)
