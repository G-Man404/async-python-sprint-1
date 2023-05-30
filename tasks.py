from concurrent.futures import ThreadPoolExecutor
import json

import utils
from external.client import *
from external.analyzer import *


class DataFetchingTask:
    def __init__(self, cities: dict):
        self.cities = cities
        self.cities_weather = []

    def get_weather_by_url(self, city: str, url: str):
        weather_in_city = YandexWeatherAPI.get_forecasting(url)
        weather_in_city_json = json.loads(weather_in_city)
        self.cities_weather.append([city, weather_in_city_json])

    def update_weather_date(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            for i in self.cities.items():
                pool.submit(self.get_weather_by_url, i[0], i[1])
            pool.shutdown(wait=True)

    def get_weather_date(self):
        self.update_weather_date()
        return self.cities_weather


class DataCalculationTask:
    def __init__(self, weather_data: list):
        self.weather_data = weather_data
        self.analyzed_data = []

    def calculation(self):
        treads = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            for weather_day in self.weather_data:
                treads.append(pool.submit(analyze_json, weather_day))
        for tread in treads:
            self.analyzed_data.append(tread.result())


class DataAggregationTask:
    pass


class DataAnalyzingTask:
    pass
