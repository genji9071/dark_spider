from pydantic import BaseModel

from vo.weibo.SpiderWeiboUserInfoVO import SpiderWeiboUserInfoVO


class SpiderWeiboVideoInfoVO(BaseModel):
    mid: str = None
    source_name: str = None
    user_info: SpiderWeiboUserInfoVO = None
    title: str = None
    content_text: str = None
    approximately_play_count: str = None
    forward_count: int = None
    comments_count: int = None
    liked_count: int = None
    watch_later_count: int = None
    video_url: str = None
    video_cover_url: str = None
    from_url: str = None
