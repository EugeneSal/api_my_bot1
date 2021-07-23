import logging
import os
import time
import requests
import telegram
import datetime as dt
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from dotenv import load_dotenv
import sqlite3

conn = sqlite3.connect("mydb.sqlite", check_same_thread=False)
# или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
load_dotenv()

TORR = 133.3223684
TOKEN = os.getenv('WEATHER_API')
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/{}'
updater = Updater(TELEGRAM_TOKEN, use_context=True)
bot = telegram.Bot(TELEGRAM_TOKEN)

city_name = '52.48, 108.00'
WEATHER_URL_4_DAYS = 'https://api.openweathermap.org/data/2.5/forecast?q=' \
                     '{}&units={}&appid={}'  # &lang=ru
WEATHER_URL = f'https://wttr.in/{city_name}'
UNITS = {'format': 2,
         'M': '',
         'Q': '',
         'lang': 'ru'}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log'
)
logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('main.log')
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter(
    '%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
logger.addHandler(c_handler)
logger.addHandler(f_handler)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    # хотел же еще сразу сделать переменную, но что то пошло не так))
    if homework_status == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    elif homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework_status == 'reviewing':
        verdict = 'Работа провереятся.'
    else:
        verdict = 'не известный статус работы'
        logger.error('не известный статус работы')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    # Оки доки))
    url = URL.format('user_api/homework_statuses/')
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            url,
            headers=headers,
            params={'from_date': current_timestamp})
        return homework_statuses.json()
    except Exception as e:
        send_message(f'Сообщение не получилось отправить: {e}')
        logger.error('Exception occurred', exc_info=True)


def send_message(message):
    logger.info(message)
    return bot.send_message(CHAT_ID, message)


def what_weather(city):
    response = requests.get(WEATHER_URL, params=UNITS)
    if response.status_code == 200:
        return f'Погода в Кике: {response.text.strip()}'
    else:
        return '<ошибка на сервере>'


def weather_send(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=what_weather(city_name))


def weather_30_hours(update, context):
    chat = update.effective_chat
    city_name = 'Kika'
    units = 'metric'
    r4 = requests.get(WEATHER_URL_4_DAYS.format(city_name, units, TOKEN)).json()

    d1 = {
        'north': '↑',
        'northeast': '↗',
        'northwest': '↖',
        'west': '←',
        'east': '→',
        'south': '↓',
        'southeast': '↘',
        'southwest': '↙',
    }
    counts1 = 10
    text1 = f"Погода в н.п. - {r4['city']['name']} на {counts1*3} часов:"

    send_message(text1)
    # print(r4['city']['name'])
    r4 = r4['list']
    counts = 0
    for resp in r4:

        if counts == counts1:
            break
        wind_direction = int(resp['wind']['deg'])
        counts += 1
        wd_favour = ''
        if 20 > wind_direction >= 0 or 360 >= wind_direction >= 340:
            wd_favour = d1['north']
        elif 67 > wind_direction >= 20:
            wd_favour = d1['northeast']
        elif 112 > wind_direction >= 67:
            wd_favour = d1['east']
        elif 157 > wind_direction >= 112:
            wd_favour = d1['southeast']
        elif 202 > wind_direction >= 157:
            wd_favour = d1['south']
        elif 247 > wind_direction >= 202:
            wd_favour = d1['southwest']
        elif 292 > wind_direction >= 247:
            wd_favour = d1['west']
        elif 340 > wind_direction >= 292:
            wd_favour = d1['northwest']
        timestamp = int(resp['dt'])
        value = dt.datetime.fromtimestamp(timestamp)
        sql = "SELECT Icon FROM Atmosphere WHERE ID=?"
        des = (str(resp['weather'][0]['id']), )
        logger.debug(des)
        cursor.execute(sql, des)
        sql1 = "SELECT icon FROM Icon_list WHERE Day_icon=?"
        q1 = cursor.fetchall()[0][0]
        logger.debug(q1)
        cursor.execute(sql1, (q1, ))
        q2 = cursor.fetchall()[0][0]
        bot.send_message(
            chat_id=chat.id,
            text=(f"🕗 {value.strftime('%Y-%m-%d %H:%M')} "
                  f"⛅{resp['clouds']['all']}"
                  f"🌡{resp['main']['temp']}°С "
                  f"💧{resp['main']['humidity']}% "
                  f"P{round(float(resp['main']['pressure']) * 100 / TORR)} "
                  f"👀{round(resp['visibility'] / 1000)} км "
                  f"{q2} "
                  f"🌬{round(resp['wind']['speed'], 1)}{wd_favour} м/с"))


def main():
    current_timestamp = int(time.time())
    logger.debug('бот запущен')
    updater.dispatcher.add_handler(
        CommandHandler('weather', weather_send))
    updater.dispatcher.add_handler(
        CommandHandler('weather30', weather_30_hours))
    while True:
        try:
            updater.start_polling(poll_interval=10.0)

            home_work = get_homeworks(current_timestamp)
            new_homework = home_work.get('homeworks')
            if new_homework:
                send_message(parse_homework_status(new_homework[0]))
            current_timestamp = home_work.get('current_date')
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            logger.error(f'Бот упал с ошибкой: {e}')
            send_message(f'Бот упал с ошибкой: {e}')
            time.sleep(5 * 60)
            continue


if __name__ == '__main__':
    main()
    conn.close()
