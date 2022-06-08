## Проектное задание первого спринта

Ваша задача — проанализировать данные по погодным условиям, используя данные от API Яндекс.Погода.


---
## Описание задания

### 1. Используя API Яндекс.Погода, получить информацию о погодных условиях для указанного списка городов

Список городов и информация о них находится в переменной `CITIES` в файле [utils.py](utils.py)

Для взаимодействия с API использовать готовый класс `YandexWeatherAPI` в модуле `utils.py`

Пример работы с классом `YandexWeatherAPI` описан в <a href="#apiusingexample">инструкции</a>

Пример ответа от API для анализа находится в [файле](examples/response.json)



### 2. Для всех городов в полученном промежутке времени вычислить среднюю температуру и узнать информацию об осадках за каждый день

Условия и требования:
- среднюю температуру считаем за промежуток времени с 9 до 19 часов;
- информация о температуре для определенного дня за определенный час находится по следующему пути: `forecasts> [день]> hours> temp`
- информация об осадках для определенного дня за определенный час находится по следующему пути: `forecasts> [день]> hours> condition`

[Пример данных](examples/response-day-info.png) с информацией о температуре и осадках за день

Список вариантов погодных условий находится в таблице в блоке `condition` по [ссылке](https://yandex.ru/dev/weather/doc/dg/concepts/forecast-test.html#resp-format__forecasts)
или в [файле](examples/conditions.txt)



### 3. Обобщить полученные данные и результат сохранить в виде таблицы в текстовом файле



### 4. Проанализировать результат и сделать вывод, какой из городов наиболее благоприятен для поездки

Наиболее благоприятным городом считаем тот, в котором средняя температура за весь период времени была самой высокой и количество солнечных дней (без осадков) было максимальным



---
## Требования к решению

1. использовать концепции ООП
2. этапы решения описать в виде отдельных классов в модуле [tasks.py](tasks.py):
  - `DataFetchingTask` - получение данных через API;
  - `DataCalculationTask` - вычисление погодных параметров;
  - `DataAggregationTask` - обобщение вычисленных данных;
  - `DataAnalyzingTask` - финальный анализ и получение результата; 
3. для решения использовать как процессы, так и потоки;
4. для решения использовать как очередь, так и пул задач;
5. использовать аннотацию типов
6. предусмотреть обработку исключительных ситуаций
7. стиль кода соответствует pep8, flake8, mypy


### Рекомендации к решению:
1. логировать результаты действий
2. написанный код покрыть тестами

---

<a name="apiusingexample"></a>

## Пример использования `YandexWeatherAPI` для работы с API

```python
from utils import YandexWeatherAPI

city_name = "MOSCOW"
ywAPI = YandexWeatherAPI()
resp = ywAPI.get_forecasting(city_name)
```