from typing import List, Optional

from fastapi import APIRouter
from loguru import logger
from pydantic import Field
from pydantic.main import BaseModel

from app import GenericResponse
from services.xhs import SpiderXhsService
from utils.EventLoopManagerUtils import event_loop_manager
from vo.SpiderBaseGetInfoResponseVO import SpiderBaseGetInfoResponseVO
from vo.SpiderBaseGetVideoInfoBatchResponseVO import SpiderBaseGetVideoInfoBatchResponseVO
from vo.xhs.SpiderXhsNoteListVO import SpiderXhsNoteListVO
from vo.xhs.SpiderXhsUserInfoVO import SpiderXhsUserInfoVO

router = APIRouter(prefix='/spider/xhs')


class get_info_from_url_request(BaseModel):
    url: str = Field(..., example="http://xhslink.com/XtEoce", description="小红书笔记链接，小红书分享出去的那个就是，短的长的都行")


@router.post('/note/info', response_model=SpiderBaseGetInfoResponseVO, summary='根据单个小红书笔记链接，获取图文信息及数据', tags=['小红书'])
def get_info_from_url(item: get_info_from_url_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = event_loop_manager.run_until_complete(SpiderXhsService.get_info_from_url(item.url))
    return GenericResponse.success(result)


class get_info_from_url_batch_request(BaseModel):
    urls: List[str] = Field(..., example=["http://xhslink.com/XtEoce", "http://xhslink.com/5vMoce",
                                          " http://xhslink.com/a2opce"],
                            description="小红书笔记链接，小红书分享出去的那个就是，短的长的都行")


@router.post('/note/info/batch', response_model=SpiderBaseGetVideoInfoBatchResponseVO, summary='批量根据小红书笔记链接，获取图文信息及数据', tags=['小红书'])
def get_info_from_url_batch(item: get_info_from_url_batch_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = event_loop_manager.run_until_complete(SpiderXhsService.get_info_from_url_batch(item.urls))
    return GenericResponse.success(result)


class get_user_request(BaseModel):
    id: str = Field(..., example="5de492710000000001003d96", description="用户id，从上游结果中获取")
    auth: Optional[str] = Field("", description="授权码，这东西比较难搞，目前还处于技术调研阶段，先不管他")


@router.post('/user/info', response_model=SpiderXhsUserInfoVO, summary='内部使用——根据小红书用户id获取用户信息', tags=['小红书'])
def get_user(item: get_user_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = SpiderXhsService.get_user(item.id, item.auth)
    return GenericResponse.success(result)


class get_note_list_request(BaseModel):
    keyword: str = Field(..., example="特赞",
                         description="小红书的关键词")
    page_num: int = Field(1, description="页数，分页查询")
    auth: Optional[str] = Field("", description="授权码，这东西比较难搞，目前还处于技术调研阶段，先不管他")


@router.post('/note/list', response_model=SpiderXhsNoteListVO, summary='内部使用——根据关键词搜索小红书笔记', tags=['小红书'])
def get_note_list(item: get_note_list_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = SpiderXhsService.get_note_list(item.keyword, item.page_num, item.auth)
    return GenericResponse.success(result)


if __name__ == '__main__':
    print(get_note_list("三得利", 1, auth=None))
