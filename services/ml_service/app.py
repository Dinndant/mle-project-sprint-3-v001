import numpy as np
import time
from fastapi import FastAPI, Body
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge

from ml_service.handler import FastApiHandler

# создаём приложение FastAPI
app = FastAPI()

# создаём обработчик запросов для API
app.handler = FastApiHandler()

prediction_values = []

REQUEST_COUNT = Counter(
    'price_prediction_requests_total',
    'Total number of price prediction requests',
    ['endpoint']
)

PREDICTION_DURATION = Histogram(
    'price_prediction_duration_seconds',
    'Duration of price prediction processing',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]  # Customize buckets as needed
)

PREDICTION_MEDIAN = Gauge(
    'price_prediction_median',
    'Median value of all predictions',
    ['endpoint']
)

# инициализируем и запускаем экпортёр метрик
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


@app.post("/api/price/") 
def predict_price(user_id: str, model_params: dict):
    """Функция определяет цену объекта

    Args:
        user_id (str): Идентификатор пользователя.
        model_params (dict): Произвольный словарь с параметрами для модели.

    Returns:
        dict: Предсказание цены.
    """
    # Считаем количество запросов к эндпоинту
    REQUEST_COUNT.labels(endpoint="/api/price/").inc()

    start_time = time.time()

    all_params = {
            "user_id": user_id,
            "model_params": model_params
        }
    user_prediction = app.handler.handle(all_params)
    price = user_prediction["prediction"]

    prediction_values.append(price)
    if prediction_values:
        median_value = np.median(prediction_values)
        PREDICTION_MEDIAN.labels(endpoint="/api/price/").set(median_value)

    duration = time.time() - start_time
    PREDICTION_DURATION.labels(endpoint="/api/price/").observe(duration)
    return {"user_id": user_id, "prediction": price}
