import datetime
import http
import time
from pprint import pprint

import feedparser
import requests
import telebot

import AI.BASE
import actions
from actions import pick, unpick

bot_token = open("bot_token", "r", encoding="utf-8").read()


# pick("history", [])

source_list = [
    # {"name": "BBC", "url": "http://feeds.bbci.co.uk/news/technology/rss.xml"},
    {"name": "Guardian", "url": "https://www.theguardian.com/uk/technology/rss"}

]


def url_parse(source, url):
    import requests
    from bs4 import BeautifulSoup

    # Отправляем запрос и получаем содержимое страницы
    cookies = {
        # '_ga_RW7D75DF8V': 'deleted',
        '_gid': 'GA1.2.684043638.1734292427',
        '_gat_gtag_UA_55961911_1': '1',
        'session_id': 'p9OLHdw-CQpjnRGyVNvlbTNOrIwCo4SC_73I8PFFPVI.Z180bQ.JvTTkQ4_yt1RufDu8Kw70Sxmto4ZEvQyO6CrKNhe_2_S3gFXDV5-9R6Ok6j2L90p1Td3PGDAjYIMyCnROz4H0Q',
        '_ga_RW7D75DF8V': 'GS1.1.1734292427.12.1.1734292588.0.0.0',
        '_ga_B0F3Y2XW9M': 'GS1.1.1734292427.12.1.1734292588.0.0.0',
        '_ga': 'GA1.2.1380503738.1721488182',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'yi,en-US;q=0.9,en;q=0.8,ru;q=0.7,he;q=0.6',
        'cache-control': 'max-age=0',
        # 'cookie': '_ga_RW7D75DF8V=deleted; _gid=GA1.2.684043638.1734292427; _gat_gtag_UA_55961911_1=1; session_id=p9OLHdw-CQpjnRGyVNvlbTNOrIwCo4SC_73I8PFFPVI.Z180bQ.JvTTkQ4_yt1RufDu8Kw70Sxmto4ZEvQyO6CrKNhe_2_S3gFXDV5-9R6Ok6j2L90p1Td3PGDAjYIMyCnROz4H0Q; _ga_RW7D75DF8V=GS1.1.1734292427.12.1.1734292588.0.0.0; _ga_B0F3Y2XW9M=GS1.1.1734292427.12.1.1734292588.0.0.0; _ga=GA1.2.1380503738.1721488182',
        'if-none-match': '"7UA8IWG3T75vAOUhBiSUCg"',
        'priority': 'u=0, i',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Chromium";v="130", "YaBrowser";v="24.12", "Not?A_Brand";v="99", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36',
    }

    response = requests.get(url=url, cookies=cookies, headers=headers)
    if response.status_code == 200:
        html_content = response.text
    else:
        time.sleep(1)
        return url_parse(source, url)

    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    print(source)
    if source == "BBC":
        # Извлекаем основной текст статьи
        # BBC обычно использует элементы с классом 'ssrcss-11r1m41-RichTextContainer e5tfeyi6' для контента
        content = soup.find('article')
        if content:
            paragraphs = content.find_all('p')
            m = ""

            for p in paragraphs:
                m += p.text.strip()

            return m
    elif source == "Guardian":
        # Извлекаем основной текст статьи
        content = soup.find(id="maincontent")
        if content:
            msg = ""
            for p in content.find_all("p"):
                msg += "\n\n" + p.text.strip()
            return msg


def entry2image(entry):
    imgs_list = entry.get("media_content")
    if imgs_list:
        for img in imgs_list:
            if img['width'] == "460":
                return img['url']

def rss_parser():
    res = []
    history = unpick("history")
    for source in source_list:
        if source["name"] == "BBC":
            def iuy():
                try:
                    return feedparser.parse(source["url"])
                except:
                    time.sleep(10)
                    return iuy()
            result = iuy()
            for entry in result.entries:
                published_parsed = entry.get("published_parsed")
                if published_parsed:
                    published_parsed = datetime.datetime(*published_parsed[:6])
                title = entry.get("title")
                link = entry.get("link")
                media_thumbnail = entry.get("media_thumbnail")

                if all((published_parsed,
                        title,
                        link,
                        media_thumbnail)):
                    media_thumbnail_url = media_thumbnail[0]['url']
                    data4return = {"source": source["name"], "time": published_parsed, "title": title, "link": link, "media_thumbnail": media_thumbnail_url}
                    if data4return not in history:
                        if datetime.datetime.now() - data4return["time"] < datetime.timedelta(days=2):
                            history.append(data4return)
                            res.append(data4return)
        elif source["name"] == "Guardian":
            # print(source["url"])
            result = feedparser.parse(source["url"])
            for entry in result.entries:
                published_parsed = entry.get("updated_parsed")
                if published_parsed:
                    published_parsed = datetime.datetime(*published_parsed[:6])
                title = entry.get("title")
                link = entry.get("link")
                media_thumbnail = entry2image(entry)

                if all((published_parsed,
                        title,
                        link,
                        media_thumbnail)):
                    data4return = {"source": source["name"], "time": published_parsed, "title": title, "link": link, "media_thumbnail": media_thumbnail}
                    if data4return not in history:
                        if datetime.datetime.now() - data4return["time"] < datetime.timedelta(days=2):
                            history.append(data4return)
                            res.append(data4return)
    pick("history", history)

    return res


while True:
    try:
        rp = rss_parser()
        rp.reverse()
        for s in rp:
            en_data = url_parse(s['source'], s["link"])
            en_data = s["title"] + "\n\n" + en_data
            image = s["media_thumbnail"]
            if en_data:
                ai = AI.BASE.Gen()
                ai.system_instructions = [
                    {"text": AI.BASE.prompts.Instructions.summarizer}
                ]
                ai.history_add("user", f'{en_data}')

                ru_data = ai.generate()
                ru_data = ru_data.replace("#", "")
                ru_data = ru_data.replace("**", "")
                ru_data = ru_data.replace("```python", "")
                ru_data = ru_data.replace("```", "")

                ai.history_add("assistant", ru_data)

                print(image)
                print(ru_data)

                actions.send_post(token=open("bot_token", "r", encoding="utf-8").read(), channel_id=-1002332331843,
                                  message=ru_data, media=image, source_link=s["link"])
                print()

    except KeyboardInterrupt:

        break
    time.sleep(20)

