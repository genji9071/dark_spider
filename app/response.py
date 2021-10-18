"""通用返回"""
import uuid
from datetime import datetime

from fastapi.responses import JSONResponse
from loguru import logger as log
from pydantic import BaseModel


def gen_request_id():
    """
    生成全局唯一request_id
    :return:
    """
    uuid_str = str(uuid.uuid1())
    return "{}".format(uuid_str)


class GenericResponse(object):
    """
    api对外暴露统一的接口
    """

    @staticmethod
    def success(data=None, message='success', code=0):
        """
        返回成功调用方法
        :param data:
        :param message:
        :param code:
        :return:
        """
        if isinstance(data, BaseModel):
            data = data.dict()
        req_id = gen_request_id()
        obj = dict(code=str(code), message=message, desc="", request_id=req_id)
        obj['result'] = data
        obj["time"] = str(datetime.now())
        log.info("{req_id} request finish".format(req_id=req_id))
        return JSONResponse(obj)

    @classmethod
    def fail(cls, message, code=500, data=None):
        """
        返回失败调用方法
        :param message:
        :param code:
        :param data:
        :return:
        """
        return cls.success(data=data, message=message, code=code)

    @classmethod
    def exception(cls, e):
        log.exception(e.args)
        return cls.fail(code=e.code, message=e.message)
