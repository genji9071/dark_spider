from pydantic import BaseModel

from vo.weibo.SpiderWeiboUserInfoVO import SpiderWeiboUserInfoVO


class SpiderWeiboImageInfoVO(BaseModel):
    mid: str = None
    source_name: str = None
    image_url_list: list = None
    cover_url: str = None
    user_info: SpiderWeiboUserInfoVO = None
    content_text: str = None
    forward_count: int = None
    comments_count: int = None
    liked_count: int = None
    watch_later_count: int = None
    from_url: str = None
