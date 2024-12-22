import datetime
import http
import time
from pprint import pprint
import feedparser
import requests
import telebot
from bs4 import BeautifulSoup
import AI.BASE
import actions
from actions import pick, unpick
import undetected_chromedriver as uc

bot_token = open("bot_token", "r", encoding="utf-8").read()

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
        'referer': 'https://scitechdaily.com/',
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

# pick("history", [])
# pick("rss_history", [])

source_list = [
    # {"name": "BBC", "url": "http://feeds.bbci.co.uk/news/technology/rss.xml"},
    # {"name": "Guardian", "url": "https://www.theguardian.com/uk/technology/rss"},
    # {"name": "SciTechDaily", "url": "https://scitechdaily.com/news/technology/feed"},
    {"name": "techcrunch", "url": "https://techcrunch.com/feed/"},

]


def entry2image(entry):
    imgs_list = entry.get("media_content")
    if imgs_list:
        for img in imgs_list:
            if img['width'] == "460":
                return img['url']


# driver = uc.Chrome(headless=True)


while True:
    try:
        res = []
        if requests.get("https://google.com/").status_code == 200:
            for source in source_list:
                rss = actions.Rss(source["name"], source["url"])
                rp = rss.parse()
                rp.reverse()
                for s in rp:
                    # driver.get(s["link"])
                    response = requests.get(url=s["link"], cookies=cookies, headers=headers)

                    soup = BeautifulSoup(response.text, 'html.parser')

                    if s['source'] == "BBC":
                        # Извлекаем основной текст статьи
                        # BBC обычно использует элементы с классом 'ssrcss-11r1m41-RichTextContainer e5tfeyi6' для контента
                        content = soup.find('article')
                        if content:
                            paragraphs = content.find_all('p')
                            m = ""

                            for p in paragraphs:
                                m += p.text.strip()

                            en_data = m
                    elif s['source'] == "Guardian":
                        # Извлекаем основной текст статьи
                        content = soup.find(id="maincontent")
                        if content:
                            msg = ""
                            for p in content.find_all("p"):
                                msg += "\n\n" + p.text.strip()
                            en_data = msg
                    elif s['source'] == "SciTechDaily":
                        # Извлекаем основной текст статьи
                        msg = ""
                        article = soup.find_all("article")
                        if article:
                            msg = ""
                            for a in article:
                                for i in a.find_all("p"):
                                    msg += "\n\n" + i.text
                            en_data = msg
                    elif s['source'] == "techcrunch":
                        # Извлекаем основной текст статьи
                        content = soup.find('figure', class_='wp-block-post-featured-image')
                        if content:
                            img = content.find("img")
                            s["media_thumbnail"] = img.get("src")
                        paragraphs_div = soup.find('div', class_='entry-content wp-block-post-content is-layout-constrained wp-block-post-content-is-layout-constrained')
                        if paragraphs_div:
                            paragraphs = paragraphs_div.find_all('p')
                            m = ""

                            for p in paragraphs:
                                m += p.text.strip()

                            en_data = m

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

                        actions.send_post(token=open("bot_token", "r", encoding="utf-8").read(), channel_id=-1002332331843,
                                          message=ru_data, media=image, source_link=s["link"])
        else:
            print(f"[{str(datetime.datetime.now().time())}] No internet")

    except KeyboardInterrupt:

        break


    except Exception as e:
        print(f"[{str(datetime.datetime.now().time())}] Error: {e}")

    print(f"[{str(datetime.datetime.now().time())}] Next check in 60 seconds...")

    time.sleep(60)

