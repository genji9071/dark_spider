from pydantic import BaseModel


class SpiderWeiboUserInfoVO(BaseModel):
    user_id: str = None
    user_nickname: str = None
    user_weibo_count: int = None
    user_video_weibo_count: int = None
    is_verified: bool = None
    user_description: str = None
    is_male: bool = None
    fans_count: int = None
    follow_count: int = None
    location:str=None
    user_profile_url:str=None
