from pydantic import BaseModel

from vo.SpiderBaseUrlInfoVO import SpiderBaseUrlInfoVO


class SpiderBaseGetInfoResponseVO(BaseModel):
    from_url: str = None
    info: SpiderBaseUrlInfoVO = None
    failure_reason: str = None
