"""通用返回"""
import uuid
from datetime import datetime

from fastapi.responses import JSONResponse
from loguru import logger as log
from pydantic import BaseModel

from vo.script.SpiderScriptTextSearchResultVO import SpiderScriptTextSearchResultVO


def gen_request_id():
    """
    生成全局唯一request_id
    :return:
    """
    uuid_str = str(uuid.uuid1())
    return "{}".format(uuid_str)

def recursive_decode(data):
    if isinstance(data, BaseModel):
        data = data.dict()
    if isinstance(data, list):
        for data_index in range(0, len(data)):
            data[data_index] = recursive_decode(data[data_index])
    if isinstance(data, dict):
        for data_key in data:
            data[data_key] = recursive_decode(data[data_key])
    return data


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
        data = recursive_decode(data)
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

if __name__ == '__main__':
    print(GenericResponse.success([SpiderScriptTextSearchResultVO(title="asd", content="vsdvs", link="vvdfs")]))