from fastapi import APIRouter

from app import GenericResponse
from services.script import SpiderScriptService
from utils.BrowserManager import browser_manager
from utils.EventLoopManagerUtils import event_loop_manager
from vo.SpiderBaseGetVideoInfoBatchResponseVO import SpiderBaseGetVideoInfoBatchResponseVO

router = APIRouter(prefix='/spider/script')


@router.get('/refresh-browser', response_model=str, summary='运维工具，重启刷新服务内置的浏览器，当浏览器被某个无良网站的cookie污染时可以用', tags=['小工具'])
def refresh_browser():
    result = event_loop_manager.run_until_complete(browser_manager.refresh_browser())
    return GenericResponse.success(result)


@router.get('/dump-page', response_model=SpiderBaseGetVideoInfoBatchResponseVO,
            summary='压测工具，开n个n秒延迟的网页，看看服务的吞吐量（以及服务器的吞吐量- -）', tags=['小工具'])
def get_dump_pages(pages_count: int, time_second: int):
    result = event_loop_manager.run_until_complete(SpiderScriptService.get_dump_pages(pages_count, time_second))
    return GenericResponse.success(result)
