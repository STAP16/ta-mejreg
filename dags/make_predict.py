
def make_predict():
	from clickhouse_connect import get_client
	import pandas as pd
	import os
	import joblib

	client = get_client(password="click", username="click", host="clickhouse", port=8123)

	dag_dir = os.path.dirname(os.path.abspath(__file__))
	model_path = os.path.join(dag_dir, 'model_speed_30.pkl')

	model = joblib.load(model_path)

	result = client.query("""
		SELECT maxOrNull(created_at) FROM v_forecast_30_60_120
	""")

	last_ts = result.result_rows[0][0]

	if pd.isna(last_ts) or last_ts is None: 
		df = client.query_df("""
		SELECT * FROM v_current_load ORDER BY minute DESC LIMIT 100
		""")
		df = df.sort_values('minute').reset_index(drop=True) # от старого к новому
		print("Таблица пустая - грузим последние 100 строк")
	else: 
		df = client.query_df(f"""
		SELECT * FROM v_current_load WHERE minute > '{last_ts.strftime('%Y-%m-%d %H:%M:%S')}'
		""")
		print(f"Инкрементальная загрузка с: {last_ts}")


	if df.empty:
		print("v_current_load пустая, нечего предсказывать")
		return

	# Генерация временных признокв
	df["minute"] = pd.to_datetime(df["minute"], dayfirst=True)
	df["hour"] = df["minute"].dt.hour
	df["dayofweek"] = df["minute"].dt.day_of_week
	df["minute"] = df["minute"].dt.minute
	df["is_weekend"] = (
			df["dayofweek"] >= 5
	).astype(int)


	#Лаговые признаки (каждые 5 мин)
	lags = [1,2,3,6,12,24]
	for lag in lags:
		df[f"speed_lag_{lag}"] = df["avg_speed"].shift(lag)
		
	df["speed_roll_mean_12"] = (
		df["avg_speed"].rolling(12).mean()
	)

	# Шаг данных - 5 минут 
	# Если 60 - 12 / 120 -  24
	future_step = 6

	df["target_speed_30"] = (
		df["avg_speed"].shift(-future_step)
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

	X = df[FEATURES]

	predicted_speed = model.predict(X)
	df["predicted_speed"] = predicted_speed
	df["predicted_load"] = df["predicted_speed"].apply(
		lambda s: 1 if s >= 50 else (2 if s >= 30 else 3)
	)

	df["horizon_min"] = 30
	df["model_version"] = "lgb_30minV1"
	columns_names = [
		"camera_id",
		"direction",
		"horizon_min",
		"predicted_load",
		"predicted_speed"
	]

	df = df.sort_values('minute')
	df = df.groupby('direction').tail(1)

	df_insert = df[columns_names]

	client.insert_df('v_forecast_30_60_120', df_insert)
	print("Предсказано: ", len(df_insert))