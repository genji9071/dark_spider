import time
from asyncio import TimeoutError

import requests
from loguru import logger
from pyppeteer.network_manager import Response

from exceptions.GeneralException import GeneralException
from utils.AsyncPool import AsyncPool
from utils.BrowserManager.BrowserPage import BrowserPage
from vo.SpiderBaseGetInfoResponseVO import SpiderBaseGetInfoResponseVO
from vo.SpiderBaseGetVideoInfoBatchResponseVO import SpiderBaseGetVideoInfoBatchResponseVO
from vo.douyin.SpiderDouyinAwemeInfoVO import SpiderDouyinAwemeInfoVO
from vo.douyin.SpiderDouyinChallengeInfoVO import SpiderDouyinChallengeInfoVO
from vo.douyin.SpiderDouyinChallengeUrlResponseVO import SpiderDouyinChallengeUrlResponseVO
from vo.douyin.SpiderDouyinUrlInfoVO import SpiderDouyinUrlInfoVO
from vo.douyin.SpiderDouyinUserInfoVO import SpiderDouyinUserInfoVO
from vo.douyin.SpiderDouyinVideoUrlByUserResponseVO import SpiderDouyinVideoUrlByUserResponseVO

TIME_OUT = 3000
RETRY_TIMES = 3


def _shift_url(url):
    if url.startswith('https://www.douyin.com/video/'):
        video_id = url.split('?')[0][len('https://www.douyin.com/video/'):]
        url = f'https://www.iesdouyin.com/share/video/{video_id}/'
    return url


async def get_info_from_url(url) -> SpiderBaseGetInfoResponseVO:
    def get_video_info_from_request(response: Response):
        if response.url.startswith("https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids="):
            nonlocal video_info_response
            video_info_response = response
            return True
        else:
            return False

    result = SpiderBaseGetInfoResponseVO()
    result.from_url = url
    for i in range(0, RETRY_TIMES):
        logger.info(f'the {str(i + 1)}th try...')
        try:
            async with BrowserPage(_shift_url(url), mobile_mode=True) as page:
                video_info_response = None
                page.on("response", get_video_info_from_request)
                await page.waitForResponse(lambda response: response.url.startswith(
                    "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids="), timeout=TIME_OUT)
                if video_info_response is not None:
                    logger.info(f"Caught! response code: {video_info_response.status}")
                    if video_info_response.status != 200 or not await video_info_response.text():
                        logger.error("返回结果异常，再试一次")
                        continue
                    response_json = await video_info_response.json()
                    if not response_json['item_list']:
                        message = "作品不见了"
                        result.failure_reason = message
                        return result
                    item = response_json['item_list'][0]
                    info = SpiderDouyinUrlInfoVO()
                    info.video_name = item['desc']
                    info.video_url = item['video']['play_addr']['url_list'][0]
                    info.cover_url = item['video']['cover']['url_list'][0]
                    info.comment_count = item['statistics']['comment_count']
                    info.digg_count = item['statistics']['digg_count']
                    info.share_count = item['statistics']['share_count']
                    info.video_id = item['video']['vid']
                    info.aweme_id = item['aweme_id']
                    info.author_user_id = item['author_user_id']
                    info.author_nickname = item['author']['nickname']
                    info.author_unique_id = item['author']['unique_id']
                    info.author_short_id = item['author']['short_id']
                    info.create_time = item['create_time'] * 1000
                    result.info = info
                    return result
                else:
                    message = "获取抖音video信息失败"
                    result.failure_reason = message
                    return result
        except TimeoutError as e:
            logger.error(e)
            continue
        except Exception as e:
            logger.exception(e)
            message = str(e)
            result.failure_reason = message
            return result
    message = "获取抖音video信息失败"
    result.failure_reason = message
    return result


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


async def get_info_from_challenge_url(url: str, maximum: int) -> SpiderDouyinChallengeUrlResponseVO:
    def get_challenge_info_from_request(response: Response):
        if response.url.startswith("https://www.iesdouyin.com/web/api/v2/challenge/info"):
            nonlocal challenge_info_response
            challenge_info_response = response
            return True
        else:
            return False

    def get_aweme_list_from_request(response: Response):
        if response.url.startswith("https://www.iesdouyin.com/web/api/v2/challenge/aweme"):
            nonlocal aweme_list_response
            aweme_list_response = response
            return True
        else:
            return False

    def event_handler(response: Response):
        nonlocal challenge_info_response
        if not challenge_info_response:
            get_challenge_info_from_request(response)
        nonlocal aweme_list_response
        if not aweme_list_response:
            get_aweme_list_from_request(response)
        return challenge_info_response and aweme_list_response

    result = SpiderDouyinChallengeUrlResponseVO()
    for i in range(0, RETRY_TIMES):
        logger.info(f'the {str(i + 1)}th try...')
        try:
            async with BrowserPage(url, mobile_mode=True) as page:
                challenge_info_response = None
                aweme_list_response = None
                page.on("response", event_handler)
                await page.waitForResponse(lambda response: response.url.startswith(
                    "https://www.iesdouyin.com/web/api/v2/challenge/aweme"), timeout=TIME_OUT)
                if challenge_info_response is not None and aweme_list_response is not None:
                    # treat challenge info
                    challenge_info_json = await challenge_info_response.json()
                    if challenge_info_json['status_code'] != 0:
                        raise GeneralException("获取抖音challenge info信息失败")
                    challenge_info_raw = challenge_info_json['ch_info']
                    challenge_info = SpiderDouyinChallengeInfoVO()
                    challenge_info.challenge_name = challenge_info_raw['cha_name']
                    challenge_info.challenge_id = challenge_info_raw['cid']
                    challenge_info.challenge_description = challenge_info_raw['desc']
                    challenge_info.user_count = challenge_info_raw['user_count']
                    challenge_info.view_count = challenge_info_raw['view_count']
                    result.challenge_info = challenge_info

                    # treat aweme list
                    aweme_list = []
                    has_more = True
                    aweme_list_info = await aweme_list_response.json()
                    while has_more:
                        if aweme_list_info['status_code'] != 0:
                            raise GeneralException("获取抖音challenge aweme list信息失败")
                        aweme_list_info_raw = aweme_list_info['aweme_list']
                        for aweme_info_raw in aweme_list_info_raw:
                            aweme_info = SpiderDouyinAwemeInfoVO()
                            aweme_info.aweme_url = aweme_info_raw['share_url']
                            aweme_info.aweme_id = aweme_info_raw['aweme_id']
                            aweme_info.video_name = aweme_info_raw['share_info']['share_title']
                            aweme_info.video_id = aweme_info_raw['video']['vid']
                            aweme_info.video_url = aweme_info_raw['video']['play_addr']['url_list'][0]
                            aweme_info.author_user_id = aweme_info_raw['author_user_id']
                            aweme_info.author_unique_id = aweme_info_raw['author']['unique_id']
                            aweme_info.author_short_id = aweme_info_raw['author']['short_id']
                            aweme_info.create_time = aweme_info_raw['create_time'] * 1000
                            aweme_list.append(aweme_info)
                        has_more = aweme_list_info['has_more'] and len(aweme_list) < maximum
                        cursor = aweme_list_info['cursor']
                        if has_more:
                            request = aweme_list_response.request
                            url = request.url.replace(f'cursor=0', f'cursor={cursor + 9}')
                            aweme_list_info = requests.get(url, headers=request.headers).json()
                    result.aweme_list = aweme_list
                    return result
                else:
                    raise GeneralException("获取抖音challenge信息失败")
        except TimeoutError as e:
            logger.error(e)
            continue
        except Exception as e:
            logger.exception(e)
            raise e
        raise GeneralException("获取抖音challenge信息失败")


def do_video_download_batch(vids: list) -> SpiderBaseGetVideoInfoBatchResponseVO:
    p_headers = {
        'authority': 'cc.oceanengine.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://cc.oceanengine.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
    }

    data = {"query_ids": vids, "water_mark": "creative_center"}

    response = requests.post('https://cc.oceanengine.com/creative_content_server/api/video/info', headers=p_headers,
                             json=data)
    data = response.json().get("data")

    result = SpiderBaseGetVideoInfoBatchResponseVO()
    result.total_count = len(data.items())
    result.success_count = len(data.items())
    result.details = list(data.values())
    return result


def get_video_list_by_user_info(user_nick_name: str, user_id: str,
                                page_num: int) -> SpiderDouyinVideoUrlByUserResponseVO:
    result = SpiderDouyinVideoUrlByUserResponseVO()
    p_headers = {
        'authority': 'cc.oceanengine.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://cc.oceanengine.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
    }

    if not user_id:
        data = {
            'order_by': 1,
            'period_type': 30,
            'search_fields': user_nick_name,
            'industry_user_type': 1,
            'keywords_type': 2
        }

        response = requests.get('https://cc.oceanengine.com/creative_radar_api/v1/douyin/author_list',
                                params=data)
        if response.status_code != 200 or response.json().get('code') != 0:
            raise GeneralException('获取抖音用户信息失败')
        data = response.json().get("data")
        if not data['items'] or data['items'][0].get('author_nickname') != user_nick_name:
            raise GeneralException('该抖音用户没有找到')
        the_author = data['items'][0]
        user_info = SpiderDouyinUserInfoVO()
        user_info.author_id = the_author['author_id']
        user_info.author_nickname = the_author['author_nickname']
        user_info.author_avatar = the_author['avatar_uri']
        user_info.is_star = the_author['is_star']
        user_info.description = the_author['signature']
        user_info.fans_count = the_author['metrics']['fans_num_all']['data']
        user_info.like_count = the_author['metrics']['like_count_all']['data']
        user_info.view_count = the_author['metrics']['vv_all']['data']
        result.user_info = user_info
        user_id = the_author['author_id']

    data = {
        'order_by': 1,
        'period_type': 30,
        'first_level_label_names': '[]',
        'second_level_label_names': '[]',
        'industry_user_type': 1,
        'limit': 50,
        'page': page_num,
        'list_type': 4,
        'list_id': user_id
    }
    response = requests.get('https://cc.oceanengine.com/creative_radar_api/v1/douyin/list', headers=p_headers,
                            params=data)
    if response.status_code != 200 or response.json().get('code') != 0:
        raise GeneralException('获取抖音视频信息失败')
    data = response.json().get("data")
    video_list = SpiderBaseGetVideoInfoBatchResponseVO()
    video_list.has_more = data['has_more']
    video_list.success_count = data['pagination']['total_count']
    details = []
    for item in data['items']:
        video = SpiderDouyinUrlInfoVO()
        video.author_nickname = item['author_nickname']
        video.video_name = item['item_title']
        video.cover_url = item['head_image_uri']
        video.comment_count = item['metrics']['comment_cnt_all']['data']
        video.digg_count = item['metrics']['like_cnt_all']['data']
        video.share_count = item['metrics']['share_cnt_all']['data']
        video.view_count = item['metrics']['vv_all']['data']
        video.video_id = item['vid']
        video.aweme_id = item['item_id']
        video.create_time = int(
            time.mktime(time.strptime(item['create_time'], "%Y-%m-%d")))
        details.append(video)
    video_list.details = details
    result.video_list = video_list
    return result


if __name__ == '__main__':
    do_video_download_batch([
        "v02033g10000c2d2n4tn0g1lglqgvll0"
    ])
