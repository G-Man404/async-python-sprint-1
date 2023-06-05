import json
import logging
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from pprint import pprint
import csv
import datetime

import utils
import external.analyzer as analyzer
import external.client as client

logging.basicConfig(
    filename='log.log',
    filemode='w',
    format='%(asctime)s: %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


class WeatherData:
    def __init__(self):
        self.cities = []
        self.json_raw_data = []
        self.json_analyzed_data = []
        self.rating = []


class DataFetchingTask:
    @staticmethod
    def update_city_weather(city: tuple[str, str]):
        city_key, city_value = city
        try:
            weather_data = client.YandexWeatherAPI.get_forecasting(city_value)
            return [city_key, weather_data]
        except:
            logging.warning(f"Failed to get data on the {city_key}")

    @staticmethod
    def update_weather_data(cities: dict):
        logging.info("data update has started")
        treads = []
        with ThreadPoolExecutor(4) as pool:
            for city in cities.items():
                tread = pool.submit(DataFetchingTask.update_city_weather, city)
                treads.append(tread)

        weather_data = []
        for tread in treads:
            weather = tread.result()
            if weather is not None:
                weather_data.append(tread.result())
        logging.info("data update completed successfully")
        return weather_data


class DataCalculationTask:
    @staticmethod
    def calculation_weather_data(json_raw_data: dict):
        logging.info("data calculation has started")
        processes = {}
        with multiprocessing.Pool() as pool:
            for city in json_raw_data:
                process = pool.apply(analyzer.analyze_json, [city[1]])
                processes[city[0]] = process
        weather_data = {}
        for city, process in processes.items():
            if len(process.keys()) != 0:
                weather_data[city] = process
        logging.info("data calculation completed successfully")
        return weather_data


class DataAggregationTask:
    @staticmethod
    def save_to_json(json_data: dict):
        logging.info("save_to_json has started")
        try:
            with open("data/weather_data.json", "w") as file:
                file.write(json.dumps(json_data))
            logging.info("save_to_json completed successfully")
        except Exception as ex:
            logging.error(ex)

    @staticmethod
    def save_to_csv(json_data: dict, city_rating: dict):
        logging.info("save_to_csv has started")
        try:
            with open("data/weather_data.csv", "w") as file:
                date_obj = json_data.get(list(json_data.keys())[0])["days"]
                date = [datetime.datetime.strptime(i["date"], '%Y-%m-%d') for i in date_obj]
                fieldnames = ["Город/день", ""]
                fieldnames.extend([d.strftime('%d-%m') for d in date])
                fieldnames.extend(["Средняя", "Рейтинг"])
                writer = csv.writer(file, delimiter=',')
                writer.writerow(fieldnames)

                for city, data in json_data.items():
                    row_1 = [city, "Температура, среднее"]
                    row_2 = ["", "Без осадков, часов"]

                    for day in data["days"]:
                        row_1.append(day["temp_avg"])
                        row_2.append(day["relevant_cond_hours"])

                    row_1.append(data["avg_temperature"])
                    row_1.append(city_rating[city])
                    row_2.append(data["avg_relevant_condition_hours"])
                    row_2.append("")

                    writer.writerow(row_1)
                    writer.writerow(row_2)
                    logging.info("save_to_csv completed successfully")


        except Exception as ex:
            logging.error(ex)


class DataAnalyzingTask:
    @staticmethod
    def analyzing(json_data: dict):
        logging.info("analyzing has started")
        rating = {}
        for city, data in json_data.items():
            rating[city] = data["avg_temperature"] - (data["avg_relevant_condition_hours"])

        city_rating = {}
        sorted_key = sorted(rating, key=rating.get)
        sorted_key.reverse()
        n = 1
        for key in sorted_key:
            city_rating[key] = n
            n += 1
        logging.info("analyzing completed successfully")
        return city_rating

if __name__ == "__main__":
    Weather = WeatherData()
    Weather.cities = utils.CITIES
    Weather.json_raw_data = DataFetchingTask.update_weather_data(Weather.cities)
    Weather.json_analyzed_data = DataCalculationTask.calculation_weather_data(Weather.json_raw_data)
    Weather.rating = DataAnalyzingTask.analyzing(Weather.json_analyzed_data)
    DataAggregationTask.save_to_csv(Weather.json_analyzed_data, Weather.rating)
    DataAggregationTask.save_to_json(Weather.json_analyzed_data)
