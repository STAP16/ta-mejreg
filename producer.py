import json
import cv2
from datetime import datetime
from ultralytics import YOLO
import boto3
from confluent_kafka import Producer

TARGET_CLASSES = {0: 'pedestrian', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
CAMERA_ID = "1"

producer = Producer({'bootstrap.servers': 'localhost:9092'})
TOPIC = "detections"

model = YOLO("yolo26n.pt")
print(model.names)
#show=True параметр, который показывает обработку видоса
results = model.track("./data/fallback2.mp4", stream=True, persist=True)

def send_message(message):
	producer.produce(TOPIC, value=message)
	producer.flush()

def create_message(obj, frame_path):
	PX_PER_METER = 40
	x1, y1, x2, y2 = obj.xyxy[0].tolist()

	message = {
		"camera_id": CAMERA_ID,
		"track_id": int(obj.id),
		"object_type": TARGET_CLASSES[int(obj.cls[0])],
		"center_x": ((x2 + x1) / 2) / PX_PER_METER,
		"center_y": ((y2 + y1) / 2) / PX_PER_METER,
		"confidence": round(float(obj.conf), 2),
		"frame_path": frame_path,
		"timestamp": datetime.now().isoformat()
	}

	return json.dumps(message)

def send_frame_to_minio(result, number):
	BUCKET_NAME = "detection-data"
	s3 = boto3.client(
		"s3",
		endpoint_url="http://localhost:9010",
		aws_access_key_id="admin",
		aws_secret_access_key="password"
	)
	response = s3.list_buckets()
	existing_buckets = [bucket['Name'] for bucket in response['Buckets']]
	if BUCKET_NAME not in existing_buckets:
		s3.create_bucket(Bucket=BUCKET_NAME)
		print("Бакет инициализирован")

	frame = result.plot()
	object_name = f'camera_{CAMERA_ID}/{datetime.now().strftime('%Y-%m-%d')}/frame_{number}.jpg'
	_, buffer = cv2.imencode(
		".jpg",
		frame,
	)

	s3.put_object(
		Bucket=BUCKET_NAME,
		Key=object_name,
		Body=buffer.tobytes()
	)
	return object_name



confidences = []
frames = 0
frame_path =f'camera_{CAMERA_ID}/{datetime.now().strftime('%Y-%m-%d')}/frame_{0}.jpg'
try: 
	for result in results: 
		frames +=1
		for obj in result.boxes:
			confidences.append(float(obj.conf))
			if int(obj.id) is None:
				continue
				
			if int(obj.cls) not in TARGET_CLASSES:
				continue
			
			message = create_message(obj, frame_path)
			send_message(message)
		if frames % 30 == 0:
			frame_path = send_frame_to_minio(result, frames)
			print("Frame sended")
			#Расчет метрик качества уверенности модели в распозновании
			avg_conf = sum(confidences) / len(confidences) if confidences else 0
			print(f"Средняя уверенность модели на данном видео: {avg_conf:.2f}")
			

except KeyboardInterrupt:
	print("Концовка")