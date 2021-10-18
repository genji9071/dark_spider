from pydantic import BaseModel


class SpiderWeiboInfoListVO(BaseModel):
    info_list: list = None
    total_count: int = None