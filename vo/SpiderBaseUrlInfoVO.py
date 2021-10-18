from pydantic import BaseModel


class SpiderBaseUrlInfoVO(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
