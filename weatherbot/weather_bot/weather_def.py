from datetime import datetime, timedelta # классы для работы с датами, временем и продолжительностью
import requests # Взаимодействие с API
from config import OPEN_WEATHER_MAP_API_KEY

# Установка эмодзи в соответствии с изменением погоды
code_to_smile_list = {
                'Clear': '\U00002600',
                'Clouds': '\U00002601',
                'Rain': '\U0001F327',
                'Drizzle': '\U00002614',
                'Thunderstorm': '\U000026A1',
                'Snow': '\U0001F328',
                'Mist': '\U0001F32B'
            }

# Получение текущего прогноза погоды
def get_current_weather(city: str):

    # Доступ к API OpenWeather
    r = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_MAP_API_KEY}&units=metric'
    )
    # Извлечение данных в формате JSON
    data = r.json()

    # Извлечение значений из JSON-объектов
    city = data['name'] + ',' + ' ' + data['sys']['country']
    temp = data['main']['temp']
    weather_description = data['weather'][0]['main']
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind = data['wind']['speed']
    feels_like = data['main']['feels_like']
    sunrise_timestamp = datetime.fromtimestamp(data['sys']['sunrise'])
    sunset_timestamp = datetime.fromtimestamp(data['sys']['sunset'])
    length_of_the_day = datetime.fromtimestamp(data['sys']['sunset']) - datetime.fromtimestamp(data['sys']['sunrise'])

    
    wd = code_to_smile_list.get(weather_description, f'\U0001F937')

    # отображение прогноза погоды пользователю
    weather_forecast = (
        f'*** {datetime.now().strftime("%a %d %b %Y, %H:%M")} ***\n'
        f'      Weather in {city}:\n\n - Temp: {temp}°C, {weather_description}{wd}\n'
        f' - Humidity: {humidity}%\n - Pressure: {pressure}mmHg\n - Wind: {wind}m/s\n'
        f' - Feels like: {feels_like}°C\n - Sunrise: {sunrise_timestamp}\n - Sunset: {sunset_timestamp}\n'
        f' - Length of the day: {length_of_the_day}'
    )
    # вернуть прогноз погоды пользователю
    return weather_forecast


# получение прогноза погоды на 24 часа
def get_24_hours_weather(city):
    # OWM выдает прогноз погоды с интервалом в 3 часа, поэтому для отображения погоды на 24 часа нам нужно отправить 8 запросов
    cnt = 8

    # доступ к API OpenWeather
    r = requests.get(
        f'https://api.openweathermap.org/data/2.5/forecast?q={city}&cnt={cnt}&appid={OPEN_WEATHER_MAP_API_KEY}&units=metric'
    )
    # извлечение значений из объектов JSON
    data = r.json()
    forecast_list = data['list']

    #  создание словаря для итерации по каждому элементу в forecast_list и извлечения временной метки для каждого элемента
    #  для преобразования данных ['dt'] в дату
    forecast_hours24 = {datetime.fromtimestamp(forecast24['dt']).date(): [] for forecast24 in forecast_list}
    for forecast24 in forecast_list:
        forecast_hours24[datetime.fromtimestamp(forecast24['dt']).date()].append(forecast24)

    forecast24_reply = f"{city} weather forecast for the next 24 hours:\n"

    # извлечение значений из объектов JSON
    for day, forecast_3hours_list in forecast_hours24.items():
        forecast24_reply += f"\n\U000025FB {day.strftime('%A, %B %d')}\n"
        for forecast_3hours in forecast_3hours_list:
            time = datetime.fromtimestamp(forecast_3hours['dt']).strftime('%I:%M %p')
            temp = forecast_3hours['main']['temp']
            wind = forecast_3hours['wind']['speed']
            feels_like = forecast_3hours['main']['feels_like']
            weather_description = forecast_3hours['weather'][0]['main']

            # получить прогноз погоды эмодзи
            wd = code_to_smile_list.get(weather_description, f'\U0001F937')

            # сбор информации о прогнозе погоды
            forecast24_reply += (
                f"{time}:\n - Temp: {temp}°C;  {weather_description}{wd}\n"
                f" - Wind: {wind}m/s;  Feels like: {feels_like}°C\n"
            )
    # вернуть прогноз погоды пользователю
    return forecast24_reply


# получение прогноза погоды на 5 дней
def get_5days_forecast(city):
    DAYS = 5
    # доступ к API OpenWeather
    r = requests.get(
        f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPEN_WEATHER_MAP_API_KEY}&units=metric'
    )
    # извлечение значений из объектов JSON
    data = r.json()
    weather_5days_list = data['list']

    # инициализация пустого списка для хранения ежедневной информации о погоде
    daily_weather = []
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) # установка части времени на 00:00:00

    # итерация для DAYS количество раз. Каждая итерация представляет день в прогнозе
    for d in range(DAYS):
        daily = []
        day = today + timedelta(days=d) # текущая дата

        #  проверка соответствия даты элемента текущему дню
        for data in weather_5days_list:
            utc_time = datetime.utcfromtimestamp(data['dt']) # текущее время UTC
            # извлечение значений из объектов JSON, если дата совпадает
            if utc_time.date() == day.date():
                temp = data['main']['temp']
                weather_description = data['weather'][0]['main']
                wind = data['wind']['speed']
                feels_like = data['main']['feels_like']
                # добавить значения в ежедневный список
                daily.append({'temp': temp, 'weather_description': weather_description, 'wind': wind, 'feels_like': feels_like})
        # расчет средних значений температуры, ветра 
        avg_temp = round(sum([d['temp'] for d in daily]) / max(1, len(daily)), 1)
        desc = daily[0]['weather_description'] if len(daily) > 0 else 'N/A'
        avg_wind = round(sum([d['wind'] for d in daily]) / max(1, len(daily)), 1)
        avg_feels_like = round(sum([d['feels_like'] for d in daily]) / max(1, len(daily)), 1)

        # добавить значения в список daily_weather
        daily_weather.append({'date': day.strftime('%A, %B %d'), 'temp': avg_temp, 'weather_description': weather_description,
                                  'wind': avg_wind, 'feels_like': avg_feels_like})

    # ответная строка с названием города и заголовком для 5-дневного прогноза погоды
    reply = f"{city} weather forecast for 5 days:\n\n"

    # получение эмодзи day_weather и сбор информации о прогнозе погоды на каждый день
    for day_weather in daily_weather:
        wd = code_to_smile_list.get(day_weather['weather_description'], f'\U0001F937')
        reply += (
            f"\U000025FB{day_weather['date']}:\n - Temp: {day_weather['temp']}°C;  {day_weather['weather_description'].capitalize()}{wd}\n" \
            f" - Wind: {day_weather['wind']}m/s;  Feels like: {day_weather['feels_like']}°C\n\n")

    # вернуть прогноз погоды пользователю
    return reply
