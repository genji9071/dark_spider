from pydantic import BaseModel


class SpiderXhsVideoInfoVO(BaseModel):
    video_url: str = None
    video_cover_url:str = None

