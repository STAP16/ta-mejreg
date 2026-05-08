CREATE TABLE IF NOT EXISTS silver_detections (
	id UInt32,
	timestamp DateTime64(3),
	camera_id String,
	track_id UInt32,
	object_type String,
	center_x Float32,
	center_y Float32,
	speed_kmh Float32,
	direction String

)
ENGINE = MergeTree()
ORDER BY (camera_id, timestamp, track_id)
PARTITION BY toYYYYMMDD(timestamp)