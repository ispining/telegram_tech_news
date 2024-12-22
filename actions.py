import datetime
import os
import random
import time
from pprint import pprint

from bs4 import BeautifulSoup

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






def normalize_content(content):
    content = content.replace("#", "")
    content = content.replace("**", "")
    content = content.replace("```python", "")
    content = content.replace("```", "")
    return content





def send_post(token, channel_id, message, media, source_link):
    try:
        bot = telebot.TeleBot(token, parse_mode="HTML")
        bot.send_photo(channel_id, media)

        k = telebot.types.InlineKeyboardMarkup()
        k.row(telebot.types.InlineKeyboardButton("Просмотреть источник", url=source_link))
        return bot.send_message(channel_id, message, reply_markup=k, disable_web_page_preview=True)
    except:
        time.sleep(5)
        return send_post(token, channel_id, message, media, source_link)


def news_check(content):
    bot = telebot.TeleBot(open("bot_token", "r", encoding="utf-8").read())

    messages = []
    last_message_id = unpick("last_message_id")
    print("start check")
    for message_id in range(last_message_id-10, last_message_id):
        message_text = bot.forward_message(1806892656, -1002332331843, message_id).text
        print(message_text)
        ai = BASE.Gen()
        ai.system_instructions = [
            {"text": "Перескажи статью буквально в несколько фраз, но крайне понятно"}
        ]
        ai.history_add("user", f'{message_text}')

        ru_data = ai.generate()
        ru_data = normalize_content(ru_data)

        messages.append(ru_data)

        time.sleep(6)

    ai2 = BASE.Gen()
    ai2.system_instructions = [
        {"text": "Твоя задача проста: Тебе отправляют статью, а ты проверяешь, есть ли она в базе статей. в базе статей предоставлены лишь краткие пересказы. Если статья есть в базе - ответчаешь 'False'. Иначе - 'True'"}
    ]
    ai2.history_add("user", f'{content}')

    return eval(ai2.generate())


class Rss:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.history = []
        if os.path.exists("rss_history"):
            self.history = unpick("rss_history")
        self.entries = None

    def bbc_parse(self, entry):
        published_parsed = entry.get("published_parsed")
        if published_parsed:
            published_parsed = datetime.datetime(*published_parsed[:6])
        title = entry.get("title")
        link = entry.get("link")
        media_thumbnail = entry.get("media_thumbnail")

        if all((published_parsed, title, link, media_thumbnail)):
            media_thumbnail_url = media_thumbnail[0]['url']
            data4return = {"source": self.name, "time": published_parsed, "title": title, "link": link,
                           "media_thumbnail": media_thumbnail_url}

            return data4return

    def guardian_parse(self, entry):
        published_parsed = entry.get("updated_parsed")
        if published_parsed:
            published_parsed = datetime.datetime(*published_parsed[:6])
        title = entry.get("title")
        link = entry.get("link")
        imgs_list = entry.get("media_content")
        media_thumbnail = None
        if imgs_list:
            for img in imgs_list:
                if img['width'] == "460":
                    media_thumbnail = img['url']

        if all((published_parsed,
                title,
                link,
                media_thumbnail)):
            data4return = {"source": self.name, "time": published_parsed, "title": title, "link": link,
                           "media_thumbnail": media_thumbnail}

            return data4return

    def scitech_parse(self, entry):
        summary = entry.get("summary")
        src = BeautifulSoup(summary, 'html.parser')
        media_thumbnail = src.find('img').get('src')
        published_parsed = entry.get("published_parsed")
        if published_parsed:
            published_parsed = datetime.datetime(*published_parsed[:6])
        link = entry.get("summary")
        link_bs = BeautifulSoup(link, 'html.parser')
        link = link_bs.find('a').get('href')
        title = entry.get("title")

        if all((published_parsed,
                title,
                link,
                media_thumbnail)):
            data4return = {"source": self.name, "time": published_parsed, "title": title, "link": link,
                           "media_thumbnail": media_thumbnail}

            return data4return

    def techcrunch_parse(self, entry):
        pprint(entry)
        published_parsed = entry.get("published_parsed")
        if published_parsed:
            published_parsed = datetime.datetime(*published_parsed[:6])
        title = entry.get("title")
        link = entry.get("link")
        media_thumbnail = "None"

        data4return = {"source": self.name, "time": published_parsed, "title": title, "link": link,
                       "media_thumbnail": media_thumbnail}
        return data4return

    def parse(self):

        import feedparser

        def iuy():
            try:
                return feedparser.parse(self.url)
            except:
                time.sleep(10)
                return iuy()

        res = []
        result = iuy()
        data4return = {}
        self.entries = result.entries

        for entry in self.entries:

            if self.name == "BBC":
                data4return = self.bbc_parse(entry)

            elif self.name == "Guardian":
                data4return = self.guardian_parse(entry)

            elif self.name == "SciTechDaily":
                data4return = self.scitech_parse(entry)

            elif self.name == "techcrunch":
                data4return = self.techcrunch_parse(entry)
            
            self.history = unpick("rss_history")

            if data4return['link'] not in self.history:
                self.history = unpick("rss_history")
                if datetime.datetime.now() - data4return["time"] < datetime.timedelta(days=2):
                    self.history.append(data4return["link"])
                    res.append(data4return)

                    pick("rss_history", self.history)

        return res




