from concurrent.futures import ThreadPoolExecutor

import utils
from external.client import *


class DataFetchingTask:
    def __init__(self, cities: dict):
        self.cities = cities
        self.cities_weather = []

    def get_weather_by_url(self, city: str, url: str):
        weather_in_city = YandexWeatherAPI.get_forecasting(url)
        self.cities_weather.append([city, weather_in_city])

    def update_weather_date(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            for i in self.cities.items():
                pool.submit(self.get_weather_by_url, i[0], i[1])
            pool.shutdown(wait=True)

    def get_weather_date(self):
        self.update_weather_date()
        return self.cities_weather


class DataCalculationTask:
    pass


class DataAggregationTask:
    pass


class DataAnalyzingTask:
    pass
