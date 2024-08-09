from aiogram import Bot, Dispatcher, types 
from aiogram.contrib.fsm_storage.memory import MemoryStorage 
from aiogram.dispatcher import FSMContext 
from aiogram.dispatcher.filters.state import State, StatesGroup 
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton 
from aiogram.utils import executor 
from config import BOT_TOKEN
from weather_def import *

# Токен API Telegram бота.
bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage() # Хранение и извлечение пользовательских данных в памяти.
dp = Dispatcher(bot, storage=storage) # Получение входящих обновлений от API Telegram Bot и маршрутизация их к соответствующим обработчикам

# Подкласс StatesGroup, используемый для хранения и извлечения данных.
class CityForecast(StatesGroup):
    now_weather = State()
    num_24hours = State()
    num_days5 = State()


quick_reply_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="now"),
            KeyboardButton(text="24 hours"),
            KeyboardButton(text="5 days")
        ]
    ],
    resize_keyboard=True
)


# Запуск бота.
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    text = "Hi there\U0001F44B I'm a weather bot. What period of time do you want to know the weather for?"
    await message.reply(text, reply_markup=quick_reply_buttons)


# Определение пользовательского ввода о периоде времени.
@dp.message_handler(lambda message: message.text in ["now", "24 hours", "5 days"], state=None)
async def get_num_days(message: types.Message):

# Получение текущего прогноза погоды.
    if message.text == "now":
      # Установка состояния беседы на "now_weather" и запрос у пользователя названия города.
        await CityForecast.now_weather.set()
        await message.reply("Please tell the name of the city you want to get the weather in")

        @dp.message_handler(state=CityForecast.now_weather) # Сохранение названия города в состоянии now_weather.
        async def current_weather(message: types.Message, state: FSMContext):
            try:
                city = message.text.capitalize()
                weather_response = get_current_weather(city)
                await message.answer(weather_response)
                await message.answer("For what period of time do you still want to know the weather?",\
                                     reply_markup=quick_reply_buttons)
                # Очистка состояния беседы после его обработки.
                await state.finish()


            except Exception as e:
                await message.reply("\U00002620 Check the city's name input plz! And try it again\U00002620\n"
                                "Or if you want to choose other time period, press /cancel")
                if message == "/cancel":
                    await state.finish()


# Получение прогноза погоды на 24 часа.
    elif message.text == "24 hours":
      # Установка состояния беседы на "now_weather" и запрос у пользователя названия города.
        await CityForecast.num_24hours.set()
        await message.reply("Please tell the name of the city you want to get the weather in")

        @dp.message_handler(state=CityForecast.num_24hours) # Сохранение названия города и штата в num_24hours
        async def get_24weather(message: types.Message, state: FSMContext):
            try:
                city = message.text.capitalize()
                weather_response = get_24_hours_weather(city)
                await message.answer(weather_response)
                await message.answer("For what period of time do you still want to know the weather?",\
                                     reply_markup=quick_reply_buttons)
                # Очистите состояние после обработки
                await state.finish()

            except Exception as e:
                await message.reply("\U00002620 Check the city's name input plz! And try it again\U00002620\n"
                                "Or if you want to choose other time period, press /cancel")
                if message == "/cancel":
                    await state.finish()


# Получение прогноза погоды на 5 дней
    elif message.text == "5 days":
      # Установка состояния разговора на "num_days5" и запрос у пользователя названия города.
        await CityForecast.num_days5.set()
        await message.reply("Please tell the name of the city you want to get the weather in")

        @dp.message_handler(state=CityForecast.num_days5)
        async def handle_city_for_5_days(message: types.Message, state: FSMContext):
            try:
                city = message.text.capitalize()
                weather_response = get_5days_forecast(city)
                await message.answer(weather_response)
                await message.answer("For what period of time do you still want to know the weather?",\
                                     reply_markup=quick_reply_buttons)
                # Очистить состояние после обработки.
                await state.finish()

            except Exception as e:
                await message.reply("\U00002620 Check the city's name input plz! And try it again\U00002620\n"
                                "Or if you want to choose other time period, press /cancel")
                if message == "/cancel":
                    await state.finish()


# Отмена выбора временного периода.
@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish() # Завершить текущее состояние.
    await message.reply(f'ОК, boss!\nWhat period of time do you still want to know the weather for?',\
                        reply_markup=quick_reply_buttons)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)