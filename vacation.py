import os
import datetime as dt
import telegram
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('WEATHER_API')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telegram.Bot(TELEGRAM_TOKEN)
DATE_VACATION = dt.datetime.strptime('25.11.2021', '%d.%m.%Y')


class OutputStringValuesDate:
    def day_string(self, days):
        days_int = days % 10
        if days_int == 0 or days_int >= 5 or (10 <= days <= 19):
            return 'дней'
        elif days_int == 1:
            return 'день'
        else:
            return 'дня'

    def mouth_string(self, month):
        if month == 1:
            return 'месяц'
        elif month < 5:
            return 'месяца'
        else:
            return 'месяцев'

    def hours_string(self, hours):
        hours_int = hours % 10
        if hours_int == 0 or hours_int >= 5 or (10 <= hours <= 19):
            return 'часов'
        elif hours_int == 1:
            return 'час'
        else:
            return 'часа'

    def minutes_string(self, minutes):
        minutes_int = minutes % 10
        if minutes_int == 0 or minutes_int >= 5 or (10 <= minutes <= 19):
            return 'минут'
        elif minutes_int == 1:
            return 'минута'
        else:
            return 'минуты'


def vacation(update, context):
    chat = update.effective_chat
    time = dt.datetime.now()
    difference_in_time = DATE_VACATION - time
    month = difference_in_time.days // 30
    days = difference_in_time.days - (month * 30)
    hours = (difference_in_time - dt.timedelta(
        days=((month * 30) + days))).seconds//3600
    minutes = ((difference_in_time - dt.timedelta(
        days=((month * 30) + days))).seconds % 3600/60)
    date_string_value = OutputStringValuesDate()
    day_value_string = date_string_value.day_string(days)
    month_value_string = date_string_value.mouth_string(month)
    hours_value_string = date_string_value.hours_string(hours)
    minutes_value_string = date_string_value.minutes_string(minutes)
    bot.send_message(chat_id=chat.id,
                     text=f'До отпуска осталось '
                          f'{month} {month_value_string} '
                          f'{days} {day_value_string} '
                          f'{hours} {hours_value_string} '
                          f'{minutes:.0f} {minutes_value_string}')
