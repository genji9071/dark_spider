from pydantic import BaseModel


class SpiderBaseGetVideoInfoBatchResponseVO(BaseModel):
    success_count: int = None
    total_count: int = None
    has_more: bool = False
    details: list = None
