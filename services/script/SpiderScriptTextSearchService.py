import urllib.parse

import requests
from pyppeteer.errors import PageError
from pyppeteer.network_manager import Response

from exceptions.GeneralException import GeneralException
from utils.BrowserManager.BrowserPage import BrowserPage
from vo.script.SpiderScriptTextSearchResultVO import SpiderScriptTextSearchResultVO


def get_search_entities(xid, text):
    url = "https://api.jikipedia.com/go/search_entities"

    payload = {"phrase":text,"page":1,"size":60}
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

    return requests.request("POST", url, headers=headers, json=payload).json()


async def get_text_search(text: str) -> SpiderScriptTextSearchResultVO:
    def get_xid(response: Response):
        if response.url.startswith("https://api.jikipedia.com/go"):
            nonlocal search_entities_response
            search_entities_response = response
            return True
        else:
            return False
    # url = f'https://jikipedia.com/search?phrase={urllib.parse.quote_plus(text)}'
    url = "https://jikipedia.com/"
    search_entities_response: Response = None
    try:
        async with BrowserPage(url, mobile_mode=False, response_func=[get_xid], timeout=0) as page:
            pass
    except Exception:
        pass
    if not search_entities_response:
        raise GeneralException("get_text_search call failed")
    # if search_entities_response.status != 200 or not await search_entities_response.text():
    #     raise GeneralException(f"get_text_search search_entities_response.text: {search_entities_response.status}")
    xid = search_entities_response.request.headers['xid']
    response_json = get_search_entities(xid, text)
    data = response_json['data']
    if not data:
        raise GeneralException("get_text_search data not found")
    founded = filter(lambda x: x['category'] == "definition", data).__next__()
    if not founded:
        raise GeneralException("get_text_search definition not found")
    info = founded['definitions'][0]
    content = info['content']
    image_url = info['images'][0]['scaled']['path']
    id = info['id']
    return SpiderScriptTextSearchResultVO(content=content, image_url=image_url, link=f"https://jikipedia.com/definition/{str(id)}")