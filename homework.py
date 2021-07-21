import logging
import os
import time
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/{}'
bot = telegram.Bot(TELEGRAM_TOKEN)


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
    if homework.get('status') == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    elif homework.get('status') == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework.get('status') == 'reviewed':
        verdict = 'Работа провереятся.'
    else:
        verdict = 'не известный статус работы'
        logger.error('не известный статус работы')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    # или нужно было включить user_api в константу тоже?
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


def main():
    current_timestamp = int(time.time())
    logger.debug('бот запущен')
    while True:
        try:
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
