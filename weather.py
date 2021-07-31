import os
import re

import requests
import datetime as dt
import logging
import telegram
import sqlite3
from dotenv import load_dotenv

from wind_direct import wind

load_dotenv()
TOKEN = os.getenv('WEATHER_API')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# константы для команды weather функции weather_30_hours
UNITS = 'metric'
TORR = 133.3223684
WEATHER_URL_4_DAYS = ('https://api.openweathermap.org/data/2.5/forecast?q='
                      '{}&units={}&lang=ru&appid={}')
# константы для команды weathernow функции what_weather, weather_send
KIKA = '52.48, 108.00'
WEATHER_URL = 'https://wttr.in/{}'
UNITS_NOW = {'format': 2,
             'M': '',
             'Q': '',
             'lang': 'ru'}

bot = telegram.Bot(TELEGRAM_TOKEN)


def what_weather(city):
    response = requests.get(WEATHER_URL.format(city), params=UNITS_NOW)
    if response.status_code == 200:
        return f'Погода в {city}: {response.text.strip()}'
    else:
        return '<ошибка на сервере>'


def weather_send(update, context):
    chat = update.effective_chat
    keyword = ' '.join(context.args)
    hours = ''.join(re.findall(r'\d+', keyword))
    word = ' '.join(keyword.replace(hours, '').split())
    context.bot.send_message(chat_id=chat.id,
                             text=what_weather(word))


def weather_30_hours(update, context):
    keyword = ' '.join(context.args)
    hours = ''.join(re.findall(r'\d+', keyword))
    city_name = ' '.join(keyword.replace(hours, '').split())
    if hours == '':
        hours = 30
    conn = sqlite3.connect("mydb.sqlite", check_same_thread=False)
    cursor = conn.cursor()
    chat = update.effective_chat
    response_4_days = requests.get(WEATHER_URL_4_DAYS.format(
            city_name, UNITS, TOKEN)).json()
    if requests.get(WEATHER_URL_4_DAYS.format(
            city_name, UNITS, TOKEN)).json()['cod'] == '404':
        response_4_days = requests.get(WEATHER_URL_4_DAYS.format(
            'Moscow', UNITS, TOKEN)).json()
    counts1 = int(hours) // 3
    text = (f"Погода в н.п. - "
            f"{response_4_days['city']['name']} на {counts1*3} часов:")
    bot.send_message(chat_id=chat.id, text=text)
    response_4_days = response_4_days['list']
    counts = 0
    for response in response_4_days:
        if counts == counts1:
            break
        counts += 1
        timestamp = int(response['dt'])
        time_to_display = dt.datetime.fromtimestamp(timestamp)
        sql1 = "SELECT Icon FROM Atmosphere WHERE ID=?"
        weather_id = (str(response['weather'][0]['id']), )
        logging.debug(weather_id)
        cursor.execute(sql1, weather_id)
        sql_response1 = cursor.fetchall()[0][0]
        logging.debug(sql_response1)
        sql2 = "SELECT icon FROM Icon_list WHERE Day_icon=?"
        cursor.execute(sql2, (sql_response1, ))
        sql_response2 = cursor.fetchall()[0][0]
        update.message.reply_text(
            f"🕗 {time_to_display.strftime('%Y-%m-%d %H:%M')} "
            f"⛅{response['clouds']['all']}"
            f"🌡{response['main']['temp']}°С "
            f"💧{response['main']['humidity']}% "
            f"P{round(float(response['main']['pressure']) * 100 / TORR)}"
            f" 👀{round(response['visibility'] / 1000)} км "
            f"{sql_response2} "
            f"🌬{round(response['wind']['speed'], 1)}"
            f"{wind(int(response['wind']['deg']))} м/с")
    conn.close()
