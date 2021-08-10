import logging
import sys
from logging.handlers import RotatingFileHandler
import os
import time
import requests
import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from dotenv import load_dotenv
from weather import weather_send  # , weather_30_hours,
from vacation import vacation
from handler import (
    start,
    regular_choice,
    received_information,
    custom_choice,
    done)

load_dotenv()
LOCATION, HOURS = range(2)
URL = 'https://practicum.yandex.ru/api/{}'
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TO_LOG = os.path.join(BASE_DIR, 'main.log')
f_handler = RotatingFileHandler(PATH_TO_LOG, maxBytes=50000000, backupCount=5)

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
    logging.critical(token_error)
    bot.send_message(CHAT_ID, token_error)
    sys.exit()

updater = Updater(TELEGRAM_TOKEN, use_context=True)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    status = {
        'approved': 'Ревьюеру всё понравилось, работа зачтена!',
        'rejected': 'К сожалению, в работе нашлись ошибки.',
        'reviewing': 'провереятся!'}

    verdict = status.get(homework_status, 'не известный статус работы')

    if homework_status == 'reviewing':
        return f'Работа "{homework_name}"!\n\n{verdict}'

    return (f'У вас проверили работу "{homework_name}"!\n\n{verdict}\n'
            f'Комментарий: {homework.get("reviewer_comment")}')


def get_homeworks(current_timestamp):
    url = URL.format('user_api/homework_statuses/')
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            url,
            headers=headers,
            params={'from_date': current_timestamp})
    except Exception as e:
        logging.error(f'Сетевая ошибка {e}. Попробуйте позже')
        return send_message(f'Сетевая ошибка {e}. Попробуйте позже')
    if homework_statuses.status_code != 200:
        logging.error(f'Код ошибки {homework_statuses.status_code}'
                      f' Попробуйте позже')
        return send_message(f'Код ошибки {homework_statuses.status_code}'
                            f' Попробуйте позже')
    try:
        return homework_statuses.json()
    except Exception as e:
        logging.error('Что то не так с API', exc_info=True)
        return send_message(f'Что то не так с API {e}')


def send_message(message):
    logging.info(f'Сообщение <<{message}>> отправлено')
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())
    logging.debug('бот запущен')
    dispatcher = updater.dispatcher
    updater.dispatcher.add_handler(
        CommandHandler('weathernow', weather_send))
    updater.dispatcher.add_handler(
        CommandHandler('vacation', vacation))
    # updater.dispatcher.add_handler(
    #     CommandHandler('weather', weather_30_hours))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Кика|Котокель|Улан-Удэ)$'), regular_choice
                ),
                MessageHandler(Filters.regex('^в другом$'), custom_choice),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Выйти')),
                    regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Выйти')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Выйти'), done)],
    )
    dispatcher.add_handler(conv_handler)
    while True:
        try:
            updater.start_polling()  # poll_interval=5.0)
            home_work = get_homeworks(current_timestamp)
            new_homework = home_work.get('homeworks')
            if new_homework:
                send_message(parse_homework_status(new_homework[0]))
            current_timestamp = home_work.get('current_date', int(time.time()))
            updater.idle()
            time.sleep(5 * 60)  # Опрашивать раз в пять минут
        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            send_message(f'Бот упал с ошибкой: {e}')
            time.sleep(5 * 60)
            continue


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(message)s, %(levelname)s, %(name)s',
        handlers=[logging.StreamHandler(), f_handler])
    main()
