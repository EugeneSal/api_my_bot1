import logging
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
)

from weather import weather_30_hours

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
reply_keyboard = [
    ['Кика', 'Котокель'],
    ['Улан-Удэ', 'в другом'],
    ['Выйти'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = [f'{key} на {value} часов' for key, value in user_data.items()]
    return "".join(facts).join(['', ''])


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Здравствуйте Сэр, в каком н.п. хотите узнать погоду, Сэр?",
        reply_markup=markup,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Хорощо Сэр, погода в н.п. {text}, '
                              f'на сколько часов показать погоду Сэр?')
    return TYPING_REPLY


def custom_choice(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'В каком городе вывести погоду, Сэр?'
    )
    return TYPING_CHOICE


def received_information(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']
    update.message.reply_text(
        f'Погода в н.п. {facts_to_str(user_data)}, Сэр:',
        reply_markup=markup,)
    for key, value in user_data.items():
        chat_id = update.effective_chat['id']
        logging.debug(f'{key}, {value}, {user_data.items()}')
        weather_30_hours(key, value, chat_id)

    user_data.clear()
    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        f"Харошего дня, Сэр!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END
