
import pandas as pd, lightgbm as lgb
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import matplotlib.pyplot as plt
from clickhouse_connect import get_client

# client = get_client(password="click", username="click", host="localhost", port=8123)

# 1) Обучение модели.
df = pd.read_csv("traffic_camera_1_bogatyrsky_180d.csv")

# Генерация временных признокв
df["Timestamp"] = pd.to_datetime(df["Timestamp"], dayfirst=True)
df["hour"] = df["Timestamp"].dt.hour
df["dayofweek"] = df["Timestamp"].dt.day_of_week
df["minute"] = df["Timestamp"].dt.minute
df["is_weekend"] = (
    df["dayofweek"] >= 5
).astype(int)


#Лаговые признаки (каждые 5 мин)
lags = [1,2,3,6,12,24]
for lag in lags:
	df[f"speed_lag_{lag}"] = df["avg speed"].shift(lag)
	
df["speed_roll_mean_12"] = (
	df["avg speed"].rolling(12).mean()
)

# Шаг данных - 5 минут 
# Если 60 - 12 / 120 -  24
future_step = 6

df["target_speed_30"] = (
	df["avg speed"].shift(-future_step)
)
df = df.dropna()

FEATURES = [
	"hour",
	"dayofweek",
  "minute",
	"is_weekend",
	
  "speed_lag_1",
	"speed_lag_2",
	"speed_lag_3",
	"speed_lag_6",
	"speed_lag_12",
	"speed_lag_24",
	
  "speed_roll_mean_12"
]

# Теперь split на test и на train

split_index = int(len(df) * 0.8)

train_df = df[:split_index]
test_df = df[split_index:]

# Обучение модели

model_30 = lgb.LGBMRegressor(
	n_estimators=500,
	learning_rate=0.03,
	num_leaves=31
)

model_30.fit(
	train_df[FEATURES],
	train_df["target_speed_30"],
	eval_set=[
		(train_df[FEATURES], train_df["target_speed_30"]), (test_df[FEATURES], test_df["target_speed_30"])
  ],
	eval_names=["train", "valid"],
	eval_metric="mae"
)
# Рисум кривые обучения
lgb.plot_metric(model_30.evals_result_)
plt.title("LightGBM learning curves")
plt.tight_layout()
plt.savefig("lgb_training.png", dpi=300)
plt.close()
print("График сохранён: lgb_training.png")


preds = model_30.predict(
	test_df[FEATURES]
)

joblib.dump(
	model_30,
	"models/model_speed_30.pkl"
)

mae = mean_absolute_error(test_df["target_speed_30"], preds)
print(mae)