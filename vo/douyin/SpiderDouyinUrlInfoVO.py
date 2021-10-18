from vo.SpiderBaseUrlInfoVO import SpiderBaseUrlInfoVO


class SpiderDouyinUrlInfoVO(SpiderBaseUrlInfoVO):
    video_name: str = None
    video_url: str = None
    cover_url: str = None
    comment_count: int = None
    digg_count: int = None
    share_count: int = None
    view_count: int = None
    video_id: str = None
    aweme_id: str = None
    author_user_id: int = None
    author_nickname: str = None
    author_unique_id: str = None
    author_short_id: str = None
    create_time: int = None
