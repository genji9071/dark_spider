import time
from typing import List, Optional

from fastapi import APIRouter
from loguru import logger
from pydantic import Field
from pydantic.main import BaseModel

from app import GenericResponse
from services.douyin import SpiderDouyinService
from utils.EventLoopManagerUtils import event_loop_manager
from vo.SpiderBaseGetInfoResponseVO import SpiderBaseGetInfoResponseVO
from vo.SpiderBaseGetVideoInfoBatchResponseVO import SpiderBaseGetVideoInfoBatchResponseVO
from vo.douyin.SpiderDouyinAwemeInfoVO import SpiderDouyinAwemeInfoVO
from vo.douyin.SpiderDouyinChallengeUrlResponseVO import SpiderDouyinChallengeUrlResponseVO

router = APIRouter(prefix='/spider/douyin')


class do_video_url_info_request(BaseModel):
    url: str = Field(..., example="https://v.douyin.com/dau87VA/", description="抖音视频链接，在抖音app中点分享获取")


@router.post('/video-url/info', response_model=SpiderBaseGetInfoResponseVO, summary='根据单个抖音视频链接获取视频信息', tags=['抖音'])
def do_video_url_info(item: do_video_url_info_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = event_loop_manager.run_until_complete(SpiderDouyinService.get_info_from_url(item.url))
    return GenericResponse.success(result)


class do_video_url_info_batch_request(BaseModel):
    urls: List[str] = Field(..., example=["https://v.douyin.com/dau87VA/", "https://v.douyin.com/dauaTkv/"],
                            description="抖音视频链接，在抖音app中点分享获取")


@router.post('/video-url/info/batch', response_model=SpiderBaseGetVideoInfoBatchResponseVO, summary='批量根据抖音视频链接获取视频信息',
             tags=['抖音'])
def do_video_url_info_batch(item: do_video_url_info_batch_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = event_loop_manager.run_until_complete(SpiderDouyinService.get_info_from_url_batch(item.urls))
    return GenericResponse.success(result)


class do_challenge_url_info_request(BaseModel):
    url: str = Field(..., example="https://v.douyin.com/dau9sP8/", description="抖音话题链接，不清楚的话可以打开例子链接看看")
    maximum: int = Field(..., example=50, description="按抖音热门默认排序，拿前n个")


@router.post('/challenge-url/info', response_model=SpiderDouyinChallengeUrlResponseVO,
             summary='根据一个抖音话题（就是关键词为#开头的抖音链接）抓取前n个抖音视频url', tags=['抖音'])
def do_challenge_url_info(
        item: do_challenge_url_info_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = event_loop_manager.run_until_complete(
        SpiderDouyinService.get_info_from_challenge_url(item.url, item.maximum))
    return GenericResponse.success(result)


class do_video_download_batch_request(BaseModel):
    vids: List[str] = Field(..., example=["v0200f230000btm60nq3m6pr6pupjer0", "v0200f180000bc06jcs1n3eabpgf6elg"],
                            description="抖音视频vid，一般由上游或者爬虫客提供")


@router.post('/video/download/batch', response_model=SpiderBaseGetVideoInfoBatchResponseVO,
             summary='批量根据抖音视频的vid下载无水印版的抖音视频', tags=['抖音'])
def do_video_download_batch(item: do_video_download_batch_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = SpiderDouyinService.do_video_download_batch(item.vids)
    return GenericResponse.success(result)


class get_video_list_by_user_info_request(BaseModel):
    user_nick_name: str = Field(..., example="一栗小莎子",
                                description="抖音账号昵称，可千万不要给错了")
    user_id: Optional[str] = Field('',
                                   description="抖音账号id, 不知道的话可以不填，看返回结果里，调下一页或者下次调的时候直接给id就可以少拿一次用户信息")
    page_num: Optional[int] = Field(1, example=1,
                                    description="页数，默认拿第一页，一页50个")


@router.post('/video-url/get-by-user', response_model=List[SpiderDouyinAwemeInfoVO],
             summary='根据抖音用户昵称获取视频列表和数据', tags=['抖音'])
def get_video_list_by_user_info(item: get_video_list_by_user_info_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = SpiderDouyinService.get_video_list_by_user_info(item.user_nick_name, item.user_id, item.page_num)
    return GenericResponse.success(result)


if __name__ == '__main__':
    started_at = time.monotonic()
    url = ''
    stopped_at = time.monotonic()
    print(f'任务完毕，总共耗时{stopped_at - started_at}s。')
