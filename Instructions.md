# Инструкции по запуску микросервиса

Каждая инструкция выполняется из директории репозитория mle-sprint3-completed
Если необходимо перейти в поддиректорию, напишите соотвесвтующую команду

## 1. FastAPI микросервис в виртуальном окружение
```python

cd services
# команда создания виртуального окружения
python3 -m venv venv3

# команда активации виртуального окружения
source venv3/bin/activate

# и установки необходимых библиотек в него
pip install -r requirements.txt

# команда запуска сервиса с помощью uvicorn
uvicorn ml_service.app:app --reload
```

### Пример curl-запроса к микросервису
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/price/?user_id=1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "floor": 8,
  "is_apartment": false,
  "kitchen_area": 6.0,
  "living_area": 22.0,
  "rooms": 1,
  "studio": false,
  "total_area": 33.0,
  "building_id": 6008,
  "build_year": 1965,
  "building_type_int": 4,
  "latitude": 55.72616195678711,
  "longitude": 37.52706527709961,
  "ceiling_height": 2.640000104904175,
  "flats_count": 68,
  "floors_total": 9,
  "has_elevator": true
}'
```


## 2. FastAPI микросервис в Docker-контейнере

```bash
# команда перехода в нужную директорию
cd services

# команда для создания образа микросервиса
docker image build . --tag price_service:0 -f Dockerfile_ml_service

# команда для запуска микросервиса в режиме docker container
docker container run -d -p 8002:8002 --env-file .env price_service:0
```

### Пример curl-запроса к микросервису

```bash
curl -X 'POST' \
  'http://127.0.0.1:8002/api/price/?user_id=1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "floor": 8,
  "is_apartment": false,
  "kitchen_area": 6.0,
  "living_area": 22.0,
  "rooms": 1,
  "studio": false,
  "total_area": 33.0,
  "building_id": 6008,
  "build_year": 1965,
  "building_type_int": 4,
  "latitude": 55.72616195678711,
  "longitude": 37.52706527709961,
  "ceiling_height": 2.640000104904175,
  "flats_count": 68,
  "floors_total": 9,
  "has_elevator": true
}'
```

## 3. Docker compose для микросервиса и системы моониторинга

```bash
# команда перехода в нужную директорию
cd services

# команда для запуска микросервиса в режиме docker compose
docker compose up --build
```

Адреса сервисов:
- Микросервис: http://127.0.0.1:8002/ и метрики http://127.0.0.1:8002/metrics
- Prometheus: http://127.0.0.1:9089/
- Grafana: http://127.0.0.1:3002/


### Пример curl-запроса к микросервису

```bash
curl -X 'POST' \
  'http://127.0.0.1:8002/api/price/?user_id=1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "floor": 8,
  "is_apartment": false,
  "kitchen_area": 6.0,
  "living_area": 22.0,
  "rooms": 1,
  "studio": false,
  "total_area": 33.0,
  "building_id": 6008,
  "build_year": 1965,
  "building_type_int": 4,
  "latitude": 55.72616195678711,
  "longitude": 37.52706527709961,
  "ceiling_height": 2.640000104904175,
  "flats_count": 68,
  "floors_total": 9,
  "has_elevator": true
}'
```

## 4. Скрипт симуляции нагрузки
Скрипт генерирует n (10) запросов с интервалом в i (2) секунды

```bash
cd services
# команды необходимые для запуска скрипта
source venv3/bin/activate

python3 services/test_service.py -n 10 -i 2
```

Адреса сервисов:
- Микросервис: http://127.0.0.1:8002/ и метрики http://127.0.0.1:8002/metrics
- Prometheus: http://127.0.0.1:9089/
- Grafana: http://127.0.0.1:3002/
