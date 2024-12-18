import os
import random
import time
from AI import BASE
import telebot


def pick(filename, data):
    import pickle

    with open(filename, "wb") as f:
        pickle.dump(data, f)


def unpick(filename):
    import pickle

    with open(filename, "rb") as f:
        return pickle.load(f)


def send_post(token, channel_id, message, media, source_link):
    try:
        bot = telebot.TeleBot(token, parse_mode="HTML")
        bot.send_photo(channel_id, media)

        k = telebot.types.InlineKeyboardMarkup()
        k.row(telebot.types.InlineKeyboardButton("Просмотреть источник", url=source_link))
        bot.send_message(channel_id, message, reply_markup=k, disable_web_page_preview=True)
    except:
        time.sleep(5)
        send_post(token, channel_id, message, media, source_link)
