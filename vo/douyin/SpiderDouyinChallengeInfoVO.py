from pydantic import BaseModel


class SpiderDouyinChallengeInfoVO(BaseModel):
    challenge_name: str = None
    challenge_id: str = None
    challenge_description: str = None
    user_count: int = None
    view_count: int = None
