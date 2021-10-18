from pydantic import BaseModel


class SpiderDouyinAwemeInfoVO(BaseModel):
    aweme_url: str = None
    video_name: str = None
    video_url: str = None
    video_id: str = None
    aweme_id: str = None
    author_user_id: int = None
    author_unique_id: str = None
    author_short_id: str = None
    create_time: int = None
