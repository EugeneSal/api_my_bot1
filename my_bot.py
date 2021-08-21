import logging
from logging.handlers import RotatingFileHandler
import os
import time

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
from dotenv import load_dotenv
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
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
except Exception as e:
    token_error = f'Ошибка с токенами {e}.'
    logging.error(token_error)


def main():
    logging.debug('бот запущен')
    dispatcher = updater.dispatcher
    updater.dispatcher.add_handler(
        CommandHandler('vacation', vacation))
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
            updater.idle()
        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            time.sleep(5 * 60)
            continue


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(message)s, %(levelname)s, %(name)s',
        handlers=[logging.StreamHandler(), f_handler])
    main()
