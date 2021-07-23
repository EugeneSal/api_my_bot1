import os
import requests
import datetime as dt
import logging
import telegram
import sqlite3
from dotenv import load_dotenv

from wind_direct import wind

load_dotenv()

TORR = 133.3223684
TOKEN = os.getenv('WEATHER_API')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
KIKA = '52.48, 108.00'
WEATHER_URL_4_DAYS = 'https://api.openweathermap.org/data/2.5/forecast?q=' \
                     '{}&units={}&appid={}'  # &lang=ru
WEATHER_URL = f'https://wttr.in/{KIKA}'
UNITS = {'format': 2,
         'M': '',
         'Q': '',
         'lang': 'ru'}
logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('weather.log')
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

bot = telegram.Bot(TELEGRAM_TOKEN)


def what_weather(city):
    response = requests.get(WEATHER_URL, params=UNITS)
    if response.status_code == 200:
        return f'Погода в Кике: {response.text.strip()}'
    else:
        return '<ошибка на сервере>'


def weather_send(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=what_weather(KIKA))


def weather_30_hours(update, context):
    conn = sqlite3.connect("mydb.sqlite", check_same_thread=False)
    cursor = conn.cursor()
    chat = update.effective_chat
    city_name = 'Kika'
    units = 'metric'
    r4 = requests.get(WEATHER_URL_4_DAYS.format(city_name, units, TOKEN)).json()
    counts1 = 10
    text1 = f"Погода в н.п. - {r4['city']['name']} на {counts1*3} часов:"
    bot.send_message(chat_id=chat.id, text=text1)
    r4 = r4['list']
    counts = 0
    for resp in r4:
        if counts == counts1:
            break
        counts += 1
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
                  f"🌬{round(resp['wind']['speed'], 1)}"
                  f"{wind(int(resp['wind']['deg']))} м/с"))
    conn.close()
