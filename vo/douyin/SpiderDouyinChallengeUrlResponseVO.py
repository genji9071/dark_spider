from pydantic import BaseModel

from vo.douyin.SpiderDouyinChallengeInfoVO import SpiderDouyinChallengeInfoVO


class SpiderDouyinChallengeUrlResponseVO(BaseModel):
    challenge_info: SpiderDouyinChallengeInfoVO = None
    aweme_list: list = None

