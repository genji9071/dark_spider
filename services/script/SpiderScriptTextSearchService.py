import urllib.parse
from typing import List

import bs4
import requests

from exceptions.GeneralException import GeneralException
from vo.script.SpiderScriptTextSearchResultVO import SpiderScriptTextSearchResultVO


def get_search_entities(xid, text):
    url = "https://api.jikipedia.com/go/search_entities"

    payload = {"phrase": text, "page": 1, "size": 60}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Client': 'web',
        'Client-Version': '2.7.4g',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://jikipedia.com',
        'Referer': 'https://jikipedia.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Token': '',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'XID': xid,
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    if response.status_code != 200:
        raise GeneralException(response.status_code)
    return response.json()


def get_text_search2(text: str) -> List[SpiderScriptTextSearchResultVO]:
    url = f"https://jikipedia.com/search?phrase={urllib.parse.quote_plus(text)}&category=definition"
    response = requests.request("GET", url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    tiles = soup.select(".tile")
    result = []
    for tile in tiles:
        link = tile.select_one(".title-container").attrs['href']
        response = requests.request("GET", link)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        title = tile.select_one(".title-container").text
        content = tile.select_one(".card-content").text
        image_url = None
        if soup.select_one(".show-images-img") and 'src' in soup.select_one(".show-images-img").attrs:
            image_url = soup.select_one(".show-images-img").attrs['src']
        result.append(SpiderScriptTextSearchResultVO(title=title, content=content, image_url=image_url,
                                              link=link))
    return result
