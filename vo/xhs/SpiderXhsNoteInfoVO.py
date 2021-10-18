from pydantic import BaseModel


class SpiderXhsNoteInfoVO(BaseModel):
    id: str = None
    from_url: str = None
    title: str = None
    type: str = None
    liked_count: int = None
    cover_url: str = None
    create_time_timestamp: int = None
    commented_count: int = None
    collected_count: int = None
    user_id: str = None
    user_nickname: str = None
    is_official_verified: bool = None
