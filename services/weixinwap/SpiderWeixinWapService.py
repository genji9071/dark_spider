from bs4 import BeautifulSoup, Tag

from exceptions.GeneralException import GeneralException
from utils.AsyncPool import AsyncPool
from utils.BrowserManager.BrowserPage import BrowserPage
from vo.xhs.SpiderXhsNoteListVO import SpiderXhsNoteListVO

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}


def get_vars_from_script(page_result: BeautifulSoup):
    result = {}
    var_list = str(page_result.select('script')[0].next).splitlines(keepends=True)
    for var in var_list:
        if not var.strip() or '=' not in var:
            continue
        key_and_value = var.split('=')
        key = key_and_value[0].replace('var', '').strip()
        value = key_and_value[1].replace('"', '').strip()
        if value.endswith(','):
            value = value[:-1]
        result[key] = value
    return result


async def get_note_list(keyword: str, maximum: int) -> SpiderXhsNoteListVO:
    async def get_task_result(url):
        try:
            nonlocal content_map
            contents = await get_note_info_from_url(url)
            content_map[url] = contents
        except:
            pass

    # async with BrowserPage("https://weixin.sogou.com", mobile_mode=True) as main_page:
    #     while True:
    #         await main_page.waitForSelector('#query')
    #         await main_page.type('#query', f"{str(random.random())}")
    #         await main_page.click('.btn-search')
    #         await main_page.waitFor(1000)
    #         try_anti_spider = BeautifulSoup(await main_page.content(), 'html.parser')
    #         if try_anti_spider.select_one('.anti-box'):
    #             await main_page.goBack()
    #             await main_page.waitFor(1000)
    #         else:
    #             break

    page = 1
    max_pages = None
    content_map = {}
    while True:
        url = f"https://weixin.sogou.com/weixinwap?type=2&ie=utf8&query={keyword}&page={str(page)}"
        async with BrowserPage(url,
                               mobile_mode=True) as list_page:
            # while True:
            soup = BeautifulSoup(await list_page.content(), 'html.parser')
            if soup.select_one('.anti-box'):
                raise GeneralException('哎哟！被微信技术们发现了，请稍后再试...')
                # await list_page.goto("https://weixin.sogou.com")
                # await list_page.waitFor(1000)
                # await list_page.goto(url,
                #                      mobile_mode=True)
                # else:
                #     break
            if not max_pages:
                vars = get_vars_from_script(soup)
                max_pages = int(vars['totalPages'])
            notes = []
            note_list = soup.select('.pic-list')[0]
            for note in list(list(note_list.children)[1].children):
                if not isinstance(note, Tag) or not note.select('.s2'):
                    continue
                texts = list(filter(lambda x: x != '\n', note.text.strip().splitlines(keepends=True)))
                title = texts[0].strip()
                description = texts[1].strip()
                author = note.select('.s2')[0].attrs['data-sourcename']
                url = 'https://weixin.sogou.com' + note.select('a')[0].attrs['href']
                info = {
                    'title': title,
                    'description': description,
                    'author': author,
                    'url': url
                }
                notes.append(info)
            if len(notes) < maximum and page < max_pages:
                page += 1
            else:
                break
    async with AsyncPool() as pool:
        for note in notes:
            pool.put(lambda x=note['url']: get_task_result(x))

    for note in notes:
        note['contents'] = content_map.get(note['url'])
    result = SpiderXhsNoteListVO()
    result.notes = notes
    result.total_count = len(notes)
    return result


async def get_note_info_from_url(url: str):
    contents = []
    async with BrowserPage(url, mobile_mode=True) as page:
        await page.waitForSelector('.rich_media_content')
        soup = BeautifulSoup(await page.content(), 'html.parser')
        raw_contents = soup.select_one('.rich_media_content')
        raw_p_labels = raw_contents.select('p')
        for p_label in raw_p_labels:
            # 处理图片
            if p_label.select_one('img'):
                img = p_label.select_one('img')
                img_content = {'content_type': 'IMAGE', 'img_url': img.attrs['data-src']}
                contents.append(img_content)
                continue
            # 处理文字
            else:
                text = p_label.text
                if not text.strip():
                    continue
                text_content = {'content_type': 'TEXT', 'text': text}
                contents.append(text_content)
                continue
        return contents
