from ultralytics import YOLO

model = YOLO("yolo26n.pt")
# Считает метрики на валидационной выборке COCO
metrics = model.val(data="coco8.yaml", split='val') # coco8 — это мини-версия для тестов
print(f"mAP50: {metrics.box.map50}")