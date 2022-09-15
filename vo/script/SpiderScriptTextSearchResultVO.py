from pydantic import BaseModel


class SpiderScriptTextSearchResultVO(BaseModel):
    content: str
    image_url: str
    link: str
