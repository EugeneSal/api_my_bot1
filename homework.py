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

bot = telegram.Bot(TELEGRAM_TOKEN)


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log'
)
# Хз надо это или нет
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
    if homework.get('status') != 'approved':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            url,
            headers=headers,
            params={'from_date': current_timestamp})
        return homework_statuses.json()
    except Exception as e:
        print(f'Сообщение не получилось отправить: {e}')
        logger.error('Exception occurred', exc_info=True)


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = 1625097600  # int(time.time())
    logger.debug('бот запущен')
    while True:
        try:
            home_work = get_homeworks(current_timestamp)
            if home_work.get('homeworks'):
                send_message(
                    parse_homework_status(home_work.get('homeworks')[0]))
                logger.info(
                    parse_homework_status(home_work.get('homeworks')[0]))
            current_timestamp = home_work.get('current_date')
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            send_message(f'Бот упал с ошибкой: {e}')
            time.sleep(5 * 60)
            continue


if __name__ == '__main__':
    main()
