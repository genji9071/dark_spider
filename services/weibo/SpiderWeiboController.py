import time

from fastapi import APIRouter
from loguru import logger
from pydantic import Field
from pydantic.main import BaseModel

from app import GenericResponse
from services.weibo import SpiderWeiboService
from vo.weibo.SpiderWeiboInfoListVO import SpiderWeiboInfoListVO
from vo.weibo.SpiderWeiboUserInfoVO import SpiderWeiboUserInfoVO
from vo.weibo.SpiderWeiboUserRelationshipVO import SpiderWeiboUserRelationshipVO

router = APIRouter(prefix='/spider/weibo')


class get_page_request(BaseModel):
    keyword: str = Field(..., example="鸿星尔克",
                         description="微博的关键词")
    page_num: int = Field(1, description="页数，分页查询")


@router.post('/video/list', response_model=SpiderWeiboInfoListVO, summary='根据关键词搜索微博视频，以及对应视频数据', tags=['微博'])
def get_page(item: get_page_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = SpiderWeiboService.get_video_list(item.keyword, item.page_num)
    return GenericResponse.success(result)


class get_user_request(BaseModel):
    id: str = Field(..., example="5886264332", description="用户id，从上游结果中获取")


@router.post('/user/info', response_model=SpiderWeiboUserInfoVO, summary='根据用户id获取微博的用户详情', tags=['微博'])
def get_user(item: get_user_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = SpiderWeiboService.get_user_info(item.id)
    return GenericResponse.success(result)

@router.post('/user/relationship', response_model=SpiderWeiboUserRelationshipVO, summary='根据用户id获取微博的关注粉丝列表', tags=['微博'])
def get_user_relationship(item: get_user_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = SpiderWeiboService.get_user_follows_and_fans(item.id)
    return GenericResponse.success(result)


class get_note_request(BaseModel):
    keyword: str = Field(..., example="特赞",
                         description="微博的关键词")
    page_num: int = Field(1, description="页数，分页查询")


@router.post('/image/list', response_model=SpiderWeiboInfoListVO, summary='根据关键词搜索微博文章，以及对应图文数据', tags=['微博'])
def get_note(item: get_note_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = SpiderWeiboService.get_image_list(item.keyword, item.page_num)
    return GenericResponse.success(result)


if __name__ == '__main__':
    started_at = time.monotonic()
    get_page('阿里破冰', 1)
    stopped_at = time.monotonic()
    print(f'任务完毕，总共耗时{stopped_at - started_at}s。')
