import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup

import logging
import requests
from pprint import pprint
import urllib.parse

from bs4 import BeautifulSoup

import os
from dotenv import load_dotenv
import logging
from http import HTTPStatus

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_YANDEX_IMAGE = 'https://yandex.ru/images/search?source=collections' \
                   '&rpt=imageview&url=urltofile&'
THUMBSNAP_API_KEY = os.getenv('THUMBSNAP_API_KEY')  # https://thumbsnap.com/api
THUMBSNAP_URL = 'https://thumbsnap.com/api/upload'

COUNT_OUTPUT_IMAGES = 4
TEST_URL_IMAGE = 'https://teatrzoo.ru/wp-content/uploads/2019/10' \
                 '/kak-krichat-lebedi_39.jpg'


def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Бот телеги отправил сообщение {message} ')
    except Exception as error:
        logging.error(f'Сбой в работе бота телеги: {error}')


def get_new_text():
    return f'Просто новый текст'


def new_text(update, context):
    chat = update.effective_chat
    text = update.message.text
    if 'http' in text:
        new_image(update, context)
        #print(context)
    else:
        context.bot.send_message(chat.id, f'Был отправлен текст {text}')


def get_new_image():
    return f'Просто новый текст'


def new_image(update, context):
    chat = update.effective_chat
    print(f'Просто Апдейт в new_image {update}')
    print(f'Апдейт текст в new_image {update.message.text}')
    if update.message.photo:
        for i in get_yandex_inf(TEST_URL_IMAGE):
            #print(i)
            context.bot.send_photo(chat.id, i)
    elif update.message.text:
        for i in get_yandex_inf(update.message.text):
            #print(f'Ссылка внутри текста с текстом {update.message.text}')
            context.bot.send_photo(chat.id, i)
            #print('Типо вывели сообщение в телегу')
    else:
        print('Вышли где то не там')



def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/newtext']], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}. Посмотри на текст, который я для тебя нашел',
        reply_markup=button
    )


def get_yandex_inf(url_image):
    url = f'https://yandex.ru/images/search?source=collections&rpt=imageview' \
          f'&url={url_image}'
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    similar = soup.find_all('div', class_='CbirSimilar-Thumb')
    all_string = []
    count_output_images = COUNT_OUTPUT_IMAGES

    for i in similar:
        str_ish = f"{i.find('a').get('href')}\n"
        str_edit = change_str_to_url(str_ish)
        if check_url_status(str_edit):
            all_string.append(str_edit)
            count_output_images = count_output_images - 1
        if count_output_images <= 0:
            break

    return all_string


def change_str_to_url(string: str):
    end_index = string.find('&rpt=')
    new_string = string[:end_index]
    begin_index = new_string.find('img_url') + 8
    newest_string = new_string[begin_index:]
    parsed_string = urllib.parse.unquote_plus(newest_string)
    print(parsed_string)
    if '?' in parsed_string:
        index_of_question_mark = parsed_string.find('?')
        parsed_string = parsed_string[:index_of_question_mark]
        print(f'Знак вопроса вот отсюда')
        print(parsed_string)
    #check_url_status(parsed_string)
    return parsed_string

def check_url_status(url):
    try:
        response = requests.get(url)
    except Exception as error:
        logging.error(f'Неполадки с запросом к url картинки. Ошибка: {error}')
        return False
    if response.status_code != HTTPStatus.OK:
        wrong_status_code = response.status_code
        logging.error(f'Страница {url} вернула ошибку {wrong_status_code}')
        return False
    else:
        print('Вернул урл из check_url_status')
        return True


def push_image_web():
    pass


def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newtext', new_text))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, new_text))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, new_image))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
