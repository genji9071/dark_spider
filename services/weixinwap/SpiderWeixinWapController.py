from fastapi import APIRouter
from loguru import logger
from pydantic import Field
from pydantic.main import BaseModel

from app import GenericResponse
from services.weixinwap import SpiderWeixinWapService
from utils.EventLoopManagerUtils import event_loop_manager
from vo.xhs.SpiderXhsNoteListVO import SpiderXhsNoteListVO

router = APIRouter(prefix='/spider/weixinwap')


class get_note_list_request(BaseModel):
    keyword: str = Field(..., example="特赞",
                         description="微信公众号文章的关键词")
    maximum: int = Field(10, description="获取最大文章数，由于是模糊查找，越后面越离谱，这个数字小一些较佳")


@router.post('/note/list', response_model=SpiderXhsNoteListVO, summary='根据关键词搜索微信公众号图文，抓取图文内容（不含图文投放数据）', tags=['微信公众号'])
def get_note_list(item: get_note_list_request):
    logger.info(item.json(indent=4, ensure_ascii=False))
    result = event_loop_manager.run_until_complete(
        SpiderWeixinWapService.get_note_list(item.keyword, item.maximum))
    return GenericResponse.success(result)
