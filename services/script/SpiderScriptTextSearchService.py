import urllib.parse

import bs4
import requests
from pyppeteer.network_manager import Response

from exceptions.GeneralException import GeneralException
from utils.BrowserManager.BrowserPage import BrowserPage
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


async def get_text_search(text: str) -> SpiderScriptTextSearchResultVO:
    def get_xid(response: Response):
        if response.url.startswith("https://api.jikipedia.com/go"):
            nonlocal search_entities_response
            search_entities_response = response
            return True
        else:
            return False

    url = "https://jikipedia.com/"
    search_entities_response: Response = None
    try:
        async with BrowserPage(url, mobile_mode=False, response_func=[get_xid], timeout=0, is_enable_js=False) as page:
            pass
    except Exception as ex:
        pass
    if not search_entities_response:
        raise GeneralException("get_text_search call failed")
    xid = search_entities_response.request.headers['xid']
    response_json = get_search_entities(xid, text)
    data = response_json['data']
    if not data:
        raise GeneralException("get_text_search data not found")
    founded = filter(lambda x: x['category'] == "definition", data).__next__()
    if not founded:
        raise GeneralException("get_text_search definition not found")
    info = founded['definitions'][0]
    title = info['term']['title']
    content = info['plaintext']
    image_url = None
    if info['images']:
        image_url = info['images'][0]['scaled']['path']
    id = info['id']
    return SpiderScriptTextSearchResultVO(title=title, content=content, image_url=image_url,
                                          link=f"https://jikipedia.com/definition/{str(id)}")

def get_text_search2(text: str) -> SpiderScriptTextSearchResultVO:
    url = f"https://jikipedia.com/search?phrase={urllib.parse.quote_plus(text)}&category=definition"
    response = requests.request("GET", url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    tiles = soup.select(".tile")
    link = tiles[0].select_one(".title-container").attrs['href']
    response = requests.request("GET", link)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    title = tiles[0].select_one(".title-container").text
    content = tiles[0].select_one(".card-content").text
    image_url = None
    if 'src' in soup.select_one(".show-images-img").attrs:
        image_url = soup.select_one(".show-images-img").attrs['src']
    return SpiderScriptTextSearchResultVO(title=title, content=content, image_url=image_url,
                                          link=link)