import hashlib
import time
import urllib.parse

import bs4
import requests

from exceptions.GeneralException import GeneralException
from utils.AsyncPool import AsyncPool
from utils.BrowserManager.BrowserPage import BrowserPage
from utils.EventLoopManagerUtils import event_loop_manager
from vo.SpiderBaseGetInfoResponseVO import SpiderBaseGetInfoResponseVO
from vo.SpiderBaseGetVideoInfoBatchResponseVO import SpiderBaseGetVideoInfoBatchResponseVO
from vo.xhs.SpiderXhsNoteInfoVO import SpiderXhsNoteInfoVO
from vo.xhs.SpiderXhsNoteListVO import SpiderXhsNoteListVO
from vo.xhs.SpiderXhsUrlInfoVO import SpiderXhsUrlInfoVO
from vo.xhs.SpiderXhsUserInfoVO import SpiderXhsUserInfoVO
from vo.xhs.SpiderXhsVideoInfoVO import SpiderXhsVideoInfoVO

XHS_ORI_IMG_SUFFIX = '?format/png'

default_auth = 'wxmp.f959bd74-26b0-4563-9245-2c7dce2c4115'


def sign(url):
    x_sign = 'X' + hashlib.md5((url + 'WSUDD').encode(encoding='UTF-8')).hexdigest()
    return x_sign


async def get_info_from_url_batch(urls) -> SpiderBaseGetVideoInfoBatchResponseVO:
    async def get_task_result(url):
        nonlocal details, success_count
        single_result = await get_info_from_url(url)
        if single_result.info:
            success_count += 1
        details.append(single_result)

    details = []
    success_count = 0
    result = SpiderBaseGetVideoInfoBatchResponseVO()
    result.total_count = len(urls)
    async with AsyncPool() as pool:
        for url in urls:
            pool.put(lambda x=url: get_task_result(x))
    result.success_count = success_count
    result.details = details
    return result


async def get_info_from_id(id: str) -> SpiderBaseGetInfoResponseVO:
    return await get_info_from_url(f"https://www.xiaohongshu.com/discovery/item/{id}")


async def get_info_from_url(url: str) -> SpiderBaseGetInfoResponseVO:
    result = SpiderBaseGetInfoResponseVO()
    result.from_url = url
    info = SpiderXhsUrlInfoVO()
    async with BrowserPage(url) as page:
        await page.waitForSelector('.img')
        soup = bs4.BeautifulSoup(await page.content(), 'html.parser')
        # img info
        if soup.select('.carousel'):
            imgs = soup.select('.carousel')[0].select('.slide')[0]
            article_imgs = []
            for img in imgs:
                img_url = img.contents[0].attrs['style'].replace('background-image:url(//', '')
                img_url = img_url[0:img_url.rfind('?')]
                img_url = f"https://{img_url}{XHS_ORI_IMG_SUFFIX}"
                # url_upload_response = OssUtils.img_url_upload_to_oss(img_url)
                article_imgs.append(img_url)
            info.article_imgs = article_imgs
        # video info
        if soup.select('video', _class='videocontent'):
            video_info = soup.select('video', _class='videocontent')[0].attrs
            video = SpiderXhsVideoInfoVO()
            video.video_url = video_info['src']
            video.video_cover_url = f"https:{video_info['poster']}"
            info.article_video = video
        # text info
        article_text = ""
        texts = soup.select('.content')[0]
        for text in texts.contents:
            paragraph = text.text
            if paragraph != '-':
                article_text += paragraph
            article_text += '\n'
        info.article_text = article_text.strip()
        # others
        article_info = soup.find_all('script', type='application/ld+json')[0]
        article_info = eval(str(article_info.contents[0]).strip())
        info.article_name = article_info['name']
        if 'image' in article_info:
            info.article_cover_img = article_info['image']
        elif 'thumbnailUrl' in article_info:
            info.article_cover_img = article_info['thumbnailUrl']
        info.article_create_timestemp = int(
            time.mktime(time.strptime(article_info['uploadDate'], "%Y-%m-%dT%H:%M:%S")))
        info.author_profile_url = article_info['author']['url']
        info.author_name = article_info['author']['name']
        result.info = info
        return result


def get_note_list(keyword: str, page_num: int, auth: str) -> SpiderXhsNoteListVO:
    def build_note_info_vo(note: dict) -> SpiderXhsNoteInfoVO:
        note_result = SpiderXhsNoteInfoVO()
        note_result.id = note['id']
        note_result.from_url = f"https://www.xiaohongshu.com/discovery/item/{note['id']}"
        note_result.title = note['title']
        note_result.type = note['type']
        note_result.liked_count = note['likes']
        note_result.collected_count = note['collects']
        note_result.commented_count = note['comments']
        note_result.cover_url = note['cover']['url']
        note_result.user_id = note['user']['id']
        note_result.user_nickname = note['user']['nickname']
        note_result.is_official_verified = note['user']['officialVerified']
        note_result.create_time_timestamp = int(time.mktime(time.strptime(note['time'], "%Y-%m-%d %H:%M")))
        return note_result

    if not auth:
        auth = default_auth
    url = f'/fe_api/burdock/weixin/v2/search/notes?keyword={urllib.parse.quote(keyword)}&sortBy=hot_desc&page={str(page_num)}&pageSize=20'
    headers = {
        'X-Sign': sign(url),
        'Content-Type': 'application/json',
        'Host': 'www.xiaohongshu.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.10(0x18000a28) NetType/4G Language/zh_CN',
        'Authorization': auth
    }
    response = requests.request("GET", "https://www.xiaohongshu.com" + url, headers=headers)
    if response.status_code == 401:
        raise GeneralException("身份验证被破，需要auth码")
    data = response.json()['data']
    result = SpiderXhsNoteListVO()
    result.total_count = data['totalCount']
    note_list = list(map(build_note_info_vo, data['notes']))
    result.notes = note_list
    return result


def get_user(id: str, auth: str) -> SpiderXhsUserInfoVO:
    if not auth:
        auth = default_auth
    url = f'/fe_api/burdock/weixin/v2/user/{str(id)}'
    headers = {
        'X-Sign': sign(url),
        'Content-Type': 'application/json',
        'Host': 'www.xiaohongshu.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.10(0x18000a28) NetType/4G Language/zh_CN',
        'Authorization': auth
    }
    response = requests.request("GET", "https://www.xiaohongshu.com" + url, headers=headers)
    if response.status_code == 401:
        raise GeneralException("身份验证被破，需要auth码")
    data = response.json()['data']
    result = SpiderXhsUserInfoVO()
    result.user_id = data['id']
    result.red_book_id = data['red_id']
    result.user_nickname = data['nickname']
    result.fans_count = data['fans']
    result.follows_count = data['follows']
    result.boards_count = data['boards']
    result.collected_count = data['collected']
    result.liked_count = data['liked']
    result.notes_count = data['notes']
    result.cover_url = data['image']
    result.location = data['location']
    result.user_description = data['desc']
    result.is_official_verified = data['officialVerified']
    result.is_male = data['gender'] == 0
    return result


if __name__ == '__main__':
    result = event_loop_manager.run_until_complete(
        get_info_from_id('60e192e8000000000102aba8'))
    print(result.json(indent=4, ensure_ascii=False))

    # result = get_user('5ad940b411be105c406bf6a8', 'wxmp.f959bd74-26b0-4563-9245-2c7dce2c4115')
    # print(result.json(indent=4, ensure_ascii=False))
