from pydantic import BaseModel


class SpiderDouyinUserInfoVO(BaseModel):
    author_id: str = None
    author_nickname: str = None
    author_avatar: str = None
    description: str = None
    is_star: bool = None

    fans_count: int = None
    like_count: int = None
    view_count: int = None
