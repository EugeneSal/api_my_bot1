import logging
from logging.handlers import RotatingFileHandler
import os
import time
import requests
import telegram
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv
from weather import weather_send, weather_30_hours
from vacation import vacation

load_dotenv()
try:
    PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
except Exception as e:
    token_error = f'Ошибка с токенами {e}.'
    logging.error(token_error)
if PRAKTIKUM_TOKEN is None or TELEGRAM_TOKEN is None or CHAT_ID is None:
    token_error = 'Не получены ТОКЕН.'
    logging.error(token_error)
    bot.send_message(CHAT_ID, token_error)
URL = 'https://praktikum.yandex.ru/api/{}'
updater = Updater(TELEGRAM_TOKEN, use_context=True)


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s, %(message)s, %(levelname)s, %(name)s')
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
logging.getLogger("").addHandler(handler)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    status = {
        'approved': 'Ревьюеру всё понравилось, работа зачтена!',
        'rejected': 'К сожалению, в работе нашлись ошибки.',
        'reviewing': 'Работа провереятся.'}
    try:
        verdict = status[homework_status]
    except Exception as e:
        verdict = f'не известный статус работы {e}'
        logging.error(f'не известный статус работы {e}')
    return (f'У вас проверили работу "{homework_name}"!\n\n{verdict}\n'
            f'Комментарий: {homework.get("reviewer_comment")}')


def get_homeworks(current_timestamp=int(time.time())):
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
        logging.error('Exception occurred', exc_info=True)


def send_message(message):
    logging.info(message)
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())
    logging.debug('бот запущен')
    updater.dispatcher.add_handler(
        CommandHandler('weathernow', weather_send))
    updater.dispatcher.add_handler(
        CommandHandler('vacation', vacation))
    updater.dispatcher.add_handler(
        CommandHandler('weather', weather_30_hours))
    while True:
        try:
            updater.start_polling(poll_interval=15.0)
            home_work = get_homeworks(current_timestamp)
            new_homework = home_work.get('homeworks')
            if new_homework:
                send_message(parse_homework_status(new_homework[0]))
            current_timestamp = home_work.get('current_date')
            time.sleep(5 * 60)  # Опрашивать раз в пять минут
        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            send_message(f'Бот упал с ошибкой: {e}')
            time.sleep(5 * 60)
            continue


if __name__ == '__main__':
    main()
