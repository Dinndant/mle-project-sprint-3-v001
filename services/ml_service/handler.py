import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from joblib import load


class FastApiHandler:
    """Класс FastApiHandler, который обрабатывает запрос и возвращает предсказание."""

    def __init__(self):
        """Инициализация переменных класса."""

        # типы параметров запроса для проверки
        self.param_types = {
            "user_id": str,
            "model_params": dict
        }

        self.model_path = "models/catboost/model.cb"
        self.load_model(model_path=self.model_path)

        self.preprocessing_pipeline = load("models/pipeline.joblib")

        # необходимые параметры для предсказаний модели
        self.required_model_params = ['floor', 'is_apartment', 'kitchen_area', 'living_area', 'rooms',
                                      'studio', 'total_area', 'building_id', 'build_year',
                                      'building_type_int', 'latitude', 'longitude', 'ceiling_height',
                                      'flats_count', 'floors_total', 'has_elevator']
        
        self.cat_features = ['is_apartment', 'studio', 'building_id', 'building_type_int', 'has_elevator']
        self.numeric_features = ['floor', 'kitchen_area', 'living_area', 'total_area', 
                                 'rooms', 'build_year', 'ceiling_height', 'flats_count',
                                 'floors_total', 'area_ratio', 'room_density']
        self.features = [10, 11, 13, 14]

    def prepare_data(self, input_dict: dict) -> dict:
        df = pd.DataFrame([input_dict])
        bool_columns = ['is_apartment', 'studio', 'has_elevator']
        df[bool_columns] = df[bool_columns].astype(int)
        df["area_ratio"] = df["living_area"] / df["total_area"]
        df["area_ratio"] = df["area_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0)
        df["room_density"] = df["rooms"] / df["total_area"]
        df["room_density"] = df["room_density"].replace([np.inf, -np.inf], 0)

        data_numeric = self.preprocessing_pipeline.transform(df[self.numeric_features])

        processed_data = pd.DataFrame(
            np.hstack([data_numeric, df[self.cat_features].values]),
        )
        processed_data = processed_data[self.features]

        return processed_data


    def load_model(self, model_path: str):
        """Загружаем обученную модель оттока.
        Args:
            model_path (str): Путь до модели.
        """
        try:
            self.model = CatBoostRegressor()
            self.model.load_model(model_path)
        except Exception as e:
            print(f"Failed to load model: {e}")

    def predict(self, model_params: dict) -> float:
        """Предсказываем вероятность оттока.

        Args:
            model_params (dict): Параметры для модели.

        Returns:
            float — вероятность оттока от 0 до 1
        """
        return self.model.predict(model_params)[0]

    def check_required_query_params(self, query_params: dict) -> bool:
        """Проверяем параметры запроса на наличие обязательного набора.
        
        Args:
            query_params (dict): Параметры запроса.
        
        Returns:
            bool: True — если есть нужные параметры, False — иначе
        """
        if "user_id" not in query_params or "model_params" not in query_params:
            return False
        
        if not isinstance(query_params["user_id"], self.param_types["user_id"]):
            return False
                
        if not isinstance(query_params["model_params"], self.param_types["model_params"]):
            return False
        return True
    
    def check_required_model_params(self, model_params: dict) -> bool:
        """Проверяем параметры пользователя на наличие обязательного набора.
        
        Args:
            model_params (dict): Параметры пользователя для предсказания.
        
        Returns:
            bool: True — если есть нужные параметры, False — иначе
        """
        missing_params = set(self.required_model_params) - set(model_params.keys())
        if missing_params:
            print(f"Missing required parameters: {', '.join(missing_params)}")
            return False
        return True
    
    def validate_params(self, params: dict) -> bool:
        """Разбираем запрос и проверяем его корректность.
        
        Args:
            params (dict): Словарь параметров запроса.
        
        Returns:
            - **dict**: Cловарь со всеми параметрами запроса.
        """
        if self.check_required_query_params(params):
            print("All query params exist")
        else:
            print("Not all query params exist")
            return False
        
        if self.check_required_model_params(params["model_params"]):
            print("All model params exist")
        else:
            print("Not all model params exist")
            return False
        return True
        
    def handle(self, params):
        """Функция для обработки входящих запросов по API. Запрос состоит из параметров.
        
        Args:
            params (dict): Словарь параметров запроса.
        
        Returns:
            - **dict**: Словарь, содержащий результат выполнения запроса.
        """
        try:
            # валидируем запрос к API
            if not self.validate_params(params):
                print("Error while handling request")
                response = {"Error": "Problem with parameters"}
            else:
                model_params = params["model_params"]
                user_id = params["user_id"]
                print(f"Predicting for user_id: {user_id} and model_params:\n{model_params}")
                
                prepared_data = self.prepare_data(model_params)

                prediction = self.predict(prepared_data)
                print(f"PREDICTION: {prediction}")
                response = {
                    "user_id": user_id, 
                    "prediction": prediction
                }
                return response
        except Exception as e:
            print(f"Error while handling request: {e}")
            return {"Error": "Problem with request"}
        else:
            return response
