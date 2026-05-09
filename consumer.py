from confluent_kafka import Consumer
import json
from clickhouse_connect import get_client

client = get_client(password="click", username="click", host="localhost", port=8123)

CAMERA_ID = "1"

conf = {
	'bootstrap.servers': 'localhost:9092',
	'group.id': 'msys-groupioas',
	'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

consumer.subscribe(["detections"])


def insert_batch(batch: list[object]):
	columns_names = [
		'timestamp',
		'camera_id',
		'track_id',
		'confidence',
		'object_type',
		'center_x',
		'center_y',
		'frame_path'
	]
	rows = []
	for item in batch:
		row = (
		item['timestamp'],
		item['camera_id'],
		item['track_id'],
		item['confidence'],
		item['object_type'],
		item['center_x'],
		item['center_y'],
		item['frame_path']
		)
		rows.append(row)

	client.insert("bronze_detections", rows, column_names=columns_names)
	batch.clear()
	print("Вставка выполнена, batch очищен")


batch = []
try: 
	while True:
		message = consumer.poll(timeout=1.0)
		print(message)
		if message is None:
			continue

		if message.error():
			continue

		data = json.loads(message.value())
		batch.append(data)
		if len(batch) == 100:
			insert_batch(batch)
except KeyboardInterrupt:
	if len(batch) != 0:
		insert_batch(batch)

