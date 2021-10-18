from pydantic import BaseModel

from vo.SpiderBaseGetVideoInfoBatchResponseVO import SpiderBaseGetVideoInfoBatchResponseVO
from vo.douyin.SpiderDouyinUserInfoVO import SpiderDouyinUserInfoVO


class SpiderDouyinVideoUrlByUserResponseVO(BaseModel):
    user_info: SpiderDouyinUserInfoVO = None
    video_list: SpiderBaseGetVideoInfoBatchResponseVO = None
