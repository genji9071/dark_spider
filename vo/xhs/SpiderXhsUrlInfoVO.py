from vo.SpiderBaseUrlInfoVO import SpiderBaseUrlInfoVO
from vo.xhs.SpiderXhsVideoInfoVO import SpiderXhsVideoInfoVO


class SpiderXhsUrlInfoVO(SpiderBaseUrlInfoVO):
    article_name: str = None
    article_cover_img: str = None
    article_create_timestemp: int = None
    author_name: str = None
    author_profile_url: str = None
    article_text: str = None
    article_imgs: list = None
    article_video: SpiderXhsVideoInfoVO = None
