import json
import logging
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
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



class DataFetchingTask:
    @staticmethod
    def update_city_weather(city: tuple[str, str], queue: multiprocessing.Queue):
        city_key, city_value = city
        try:
            weather_data = client.YandexWeatherAPI.get_forecasting(city_value)
            queue.put([city_key, weather_data])
        except:
            logging.warning(f"Failed to get data on the {city_key}")

    @staticmethod
    def update_weather_data(cities: dict, queue: multiprocessing.Queue):
        logging.info("data update has started")
        with ThreadPoolExecutor(4) as pool:
            for city in cities.items():
                pool.submit(DataFetchingTask.update_city_weather, city, queue)


class DataCalculationTask:
    @staticmethod
    def calculation_weather_data(queue: multiprocessing.Queue):
        logging.info("data calculation has started")
        processes = {}
        with multiprocessing.Pool() as pool:
            while True:
                if queue.empty():
                    logging.info("data calculation completed successfully")
                    break
                else:
                    city = queue.get()
                    process = pool.apply(analyzer.analyze_json, [city[1]])
                    processes[city[0]] = process
        weather_data = {}
        for city, process in processes.items():
            if len(process.keys()) != 0:
                weather_data[city] = process
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
    cities = utils.CITIES
    queue = multiprocessing.Queue()
    DataFetchingTask.update_weather_data(cities, queue)
    json_analyzed_data = DataCalculationTask.calculation_weather_data(queue)
    rating = DataAnalyzingTask.analyzing(json_analyzed_data)
    DataAggregationTask.save_to_csv(json_analyzed_data, rating)
    DataAggregationTask.save_to_json(json_analyzed_data)
    logging.info(f"The most favorable city for a trip: {list(rating.keys())[0]}")
