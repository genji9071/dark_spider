from pydantic import BaseModel


class SpiderXhsUserInfoVO(BaseModel):
    fans_count: int = None
    follows_count: int = None
    is_male: bool = None
    user_id: str = None
    user_nickname: str = None
    notes_count: int = None
    boards_count: int = None
    location: str = None
    cover_url: str = None
    collected_count: int = None
    user_description: str = None
    liked_count: int = None
    is_official_verified: bool = None
    red_book_id: str = None
