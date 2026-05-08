CREATE TABLE IF NOT EXISTS bronze_detections (
	timestamp DateTime64(3),
	camera_id String,
	track_id UInt32,
	confidence Float32,
	object_type String,
	center_x Float32,
	center_y Float32,
	frame_path String
)
ENGINE = MergeTree()
ORDER BY (camera_id, timestamp, track_id)
PARTITION BY toYYYYMMDD(timestamp)