from pydantic import BaseModel


class SpiderWeiboUserRelationshipVO(BaseModel):
    follower_ids: list = []
    fan_ids: list = []
