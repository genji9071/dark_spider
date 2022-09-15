from typing import Optional

from pydantic import BaseModel


class SpiderScriptTextSearchResultVO(BaseModel):
    content: str
    image_url: Optional[str]
    link: str
