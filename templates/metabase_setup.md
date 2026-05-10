# Metabase: пошаговая настройка дашборда (Модуль В)

## 1. Подключение ClickHouse
- Админ-панель Metabase → `Add Database`
- **Database type:** ClickHouse (если нет в списке — выбрать PostgreSQL и указать порт 8123, или установить драйвер clickhouse через Plugins, НО обычно в ванильном Metabase достаточно выбрать `PostgreSQL` с `host=clickhouse`, `port=8123` — ClickHouse speak HTTP protocol. Если не заработает — используй нативный драйвер или Presto.)
- На конкурсе скорее всего Metabase уже подключен / или используй встроенный H2 и SQL-запросы через `Native query` с подключением к ClickHouse через внешний драйвер. 
- **Самый надёжный вариант на конкурсе:** `Settings → Admin → Databases → Add database → ClickHouse` (драйвер обычно предустановлен в конкурсных образах).
- Host: `localhost` или `clickhouse` (если в Docker), Port: `8123`, User: `click`, Password: `click`.

## 2. Создать 5 Questions (SQL-запросы)

### SQL-1: Текущее состояние транспортного потока (Number карточка)
```sql
SELECT 
    minute,
    vehicle_count,
    avg_speed,
    density
FROM v_current_load
WHERE camera_id = {{camera_id}}
ORDER BY minute DESC
LIMIT 1
```
- Визуализация: **Scalar** (покажет последнее значение)
- Название: «Сейчас на дороге»

### SQL-2: Структура транспортного потока (Pie / Bar)
```sql
SELECT 
    vehicle_type,
    sum(count) as total,
    avg(share_pct) as avg_share
FROM v_vehicle_structure
WHERE camera_id = {{camera_id}}
GROUP BY vehicle_type
```
- Визуализация: **Pie Chart** или **Bar**
- Название: «Состав потока»

### SQL-3: Динамика нагрузки за последний час (Line chart)
```sql
SELECT 
    minute,
    vehicle_count,
    avg_speed
FROM v_current_load
WHERE camera_id = {{camera_id}}
  AND minute >= now() - INTERVAL 1 HOUR
ORDER BY minute ASC
```
- Визуализация: **Line**
- Название: «Нагрузка (1 час)»

### SQL-4: Прогноз на 30/60/120 минут (Bar / Line)
```sql
SELECT 
    horizon_min,
    avg(predicted_load) as predicted_load,
    avg(predicted_speed) as predicted_speed
FROM v_forecast_30_60_120
WHERE camera_id = {{camera_id}}
GROUP BY horizon_min
ORDER BY horizon_min
```
- Визуализация: **Bar**
- Название: «Прогноз загрузки»

### SQL-5: Сравнение с вчера (Line — 2 серии)
```sql
SELECT 
    toDate(minute) as date,
    toHour(minute) as hour,
    avg(vehicle_count) as avg_count
FROM v_current_load
WHERE camera_id = {{camera_id}}
  AND minute >= today() - INTERVAL 1 DAY
GROUP BY date, hour
ORDER BY date, hour
```
- Визуализация: **Line** (группировка по `date` — получится 2 линии: сегодня и вчера)
- Название: «Сегодня vs Вчера»

## 3. Собрать Dashboard
- `New → Dashboard → "Транспортный поток"`
- Добавить все 5 Questions
- Добавить **Filter** → `Text or Category` → подключить к полю `camera_id` во всех вопросах
- Настроить автообновление: `... → Auto-refresh → 30 seconds`

## 4. Проверка критериев
| Критерий | Что в дашборде |
|----------|----------------|
| Данные из модуля Б/В | Все SQL читают витрины (результат модулей А и В) |
| Режим реального времени | Автообновление 30 сек + v_current_load обновляется DAG-ом |
| Ключевые метрики на 1 экране | 5 виджетов: текущее, структура, динамика, прогноз, сравнение |
| Удобная визуализация | Разные типы графиков, фильтр по камере |
| Текущее состояние | SQL-1 (Scalar) + SQL-3 (Line) |
| Прогноз | SQL-4 (Bar) |
| Сравнение с прошлым | SQL-5 (Line с 2 сериями) |
