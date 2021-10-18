import sys
import time

from fastapi import FastAPI, Request
from loguru import logger

from app.response import GenericResponse
from config import config
from exceptions.GeneralException import GeneralException
from services.douyin.SpiderDouyinController import router as douyin_router
from services.script.SpiderScriptController import router as script_route
from services.weibo.SpiderWeiboController import router as weibo_route
from services.weixinwap.SpiderWeixinWapController import router as weixinwap_route
from services.xhs.SpiderXhsController import router as xhs_router


def create_app() -> FastAPI:
    """生成FastAPI对象"""
    app = FastAPI()

    set_logger()

    register_router(app)

    register_exception(app)

    register_middleware(app)

    return app


def set_logger():
    """log初始化"""
    logger.remove()
    level = 'DEBUG' if config['env']['debug'] else 'INFO'
    logger.add(sys.stdout, level=level)
    logger.add(f'logs/error.log', level='ERROR', rotation='50 MB')


def register_router(app: FastAPI):
    """注册路由"""
    app.include_router(xhs_router)
    app.include_router(weibo_route)
    app.include_router(douyin_router)
    app.include_router(script_route)
    app.include_router(weixinwap_route)

    @app.get('/health_check')
    def health_check():
        return


def register_exception(app: FastAPI):
    """注册异常"""

    @app.exception_handler(GeneralException)
    async def base_exception_handler(request: Request, exc: GeneralException):
        """下载异常"""
        return GenericResponse.exception(exc)


def register_middleware(app: FastAPI):
    @app.middleware('http')
    async def add_process_time(request: Request, call_next):
        start_time = time.time()
        resp = await call_next(request)
        if 'OPTIONS' == request.method:
            resp.status_code = 200
            return resp
        if '/health_check' != request.url.path:
            logger.info(f'process {request.url.path} cost: {time.time() - start_time}s')
        return resp
