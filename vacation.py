import os
import datetime as dt
import telegram
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('WEATHER_API')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telegram.Bot(TELEGRAM_TOKEN)
DATE_VACATION = dt.datetime.strptime('25.11.2021', '%d.%m.%Y')


def vacation(update, context):
    chat = update.effective_chat
    time = dt.datetime.now()
    difference_in_time = DATE_VACATION - time
    difference_in_date = difference_in_time.days
    month = difference_in_date // 30
    days = difference_in_date - (month * 30)
    hours = round((difference_in_time.total_seconds()/3600) % 24)
    minutes = round((difference_in_time.seconds/3600)%60)
    # 60 - abs(round(((difference_in_time.total_seconds() / 3600) % 1140)))
    mr = minutes % 10
    hr = hours % 10
    dr = days % 10
    if dr == 0 or dr >= 5 or (10 <= days <= 19):
        d = 'дней'
    elif dr == 1:
        d = 'день'
    else:
        d = 'дня'
    if hr == 0 or hr >= 5 or (10 <= hours <= 19):
        h = 'часов'
    elif hr == 1:
        h = 'час'
    else:
        h = 'часа'
    if month == 1:
        m = 'месяц'
    elif month < 5:
        m = 'месяца'
    else:
        m = 'месяцев'
    if mr == 0 or mr >= 5 or (10 <= minutes <= 19):
        min = 'минут'
    elif mr == 1:
        min = 'минута'
    else:
        min = 'минуты'
    bot.send_message(
        chat_id=chat.id, text=f'До отпуска осталось {month} {m} {days} {d} '
                              f'{hours} {h} {minutes} {min}')
