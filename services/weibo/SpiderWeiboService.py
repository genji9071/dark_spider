import requests
import urllib3

from exceptions.GeneralException import GeneralException
from vo.weibo.SpiderWeiboImageInfoVO import SpiderWeiboImageInfoVO
from vo.weibo.SpiderWeiboInfoListVO import SpiderWeiboInfoListVO
from vo.weibo.SpiderWeiboUserInfoVO import SpiderWeiboUserInfoVO
from vo.weibo.SpiderWeiboUserRelationshipVO import SpiderWeiboUserRelationshipVO
from vo.weibo.SpiderWeiboVideoInfoVO import SpiderWeiboVideoInfoVO

urllib3.disable_warnings()

def _get_json(params):
    url = 'https://m.weibo.cn/api/container/getIndex?'
    r = requests.get(url,
                     params=params,
                     headers={
                         'User_Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
                         'Cookie': None},
                     verify=False)
    return r.json()


def _get_full_fans_list_ids_by_max(id, max):
    total = set()
    has_next = True
    page = 1
    while has_next:
        params = {
            'containerid': f'231051_-_fans_-_{id}',
            'page': page
        }
        js = _get_json(params)
        if not js['ok']:
            if 'msg' in js and js['msg'] == '这里还没有内容':
                return total
            else:
                raise GeneralException('gg')
        result = js['data']
        for card in result['cards']:
            if card.get('itemid') == f'2310510033_1_ _{id}':
                old_size = len(total)
                total = total.union(set(map(lambda x: str(x['user']['id']), card['card_group'])))
                if len(total) == old_size:
                    return total
        if len(total) >= max:
            has_next = False
        else:
            page += 1
    return total

def _get_full_followers_list_ids_by_max(id, max):
    total = set()
    has_next = True
    page = 1
    while has_next:
        params = {
            'containerid': f'231051_-_followers_-_{id}',
            'page': page
        }
        js = _get_json(params)
        if not js['ok']:
            if 'msg' in js and js['msg'] == '这里还没有内容':
                return total
            else:
                raise GeneralException('gg')
        result = js['data']
        for card in result['cards']:
            if card.get('itemid') == f'2310510024_1_ _{id}':
                old_size = len(total)
                total = total.union(set(map(lambda x: str(x['user']['id']), card['card_group'])))
                if len(total) == old_size:
                    return total
        if len(total) >= max:
            has_next = False
        else:
            page += 1
    return total

def get_video_list(keyword: str, page_num: int) -> SpiderWeiboInfoListVO:
    # type：视频=64
    type = 64
    params = {
        'containerid': f'100103type={str(type)}&q={keyword}&t=0',
        'page_type': 'searchall',
        'page': page_num
    }
    js = _get_json(params)
    if not js['ok']:
        raise GeneralException('获取微博video list信息失败')
    result = SpiderWeiboInfoListVO()
    result.total_count = js['data']['cardlistInfo']['total']
    cards = js['data']['cards']
    video_info_list = []
    for card in cards:
        if card['card_type'] == 9:
            video_info_list.append(card)
        elif 'card_group' in card:
            for inner_Card in card['card_group']:
                if inner_Card['card_type'] == 9:
                    video_info_list.append(inner_Card)
    info_list = []
    for video_info in video_info_list:
        if 'page_info' not in video_info['mblog']:
            continue
        info = SpiderWeiboVideoInfoVO()
        info.mid = video_info['mblog']['mid']
        info.source_name = video_info['mblog']['source']
        user_info = SpiderWeiboUserInfoVO()
        user_info.user_id = video_info['mblog']['user']['id']
        user_info.user_nickname = video_info['mblog']['user']['screen_name']
        user_info.user_weibo_count = video_info['mblog']['user']['statuses_count']
        user_info.is_verified = video_info['mblog']['user']['verified']
        user_info.user_description = video_info['mblog']['user']['description']
        user_info.is_male = video_info['mblog']['user']['gender'] == 'm'
        user_info.fans_count = video_info['mblog']['user']['followers_count']
        user_info.follow_count = video_info['mblog']['user']['follow_count']
        info.user_info = user_info
        info.title = video_info['mblog']['page_info']['page_title']
        info.content_text = video_info['mblog']['page_info'].get('content2')
        info.approximately_play_count = video_info['mblog']['page_info']['play_count']
        info.forward_count = video_info['mblog']['reposts_count']
        info.comments_count = video_info['mblog']['comments_count']
        info.liked_count = video_info['mblog']['attitudes_count']
        info.watch_later_count = video_info['mblog']['pending_approval_count']
        info.video_url = video_info['mblog']['page_info']['media_info']['stream_url_hd']
        info.video_cover_url = video_info['mblog']['page_info']['page_pic']['url']
        info.from_url = video_info['mblog']['page_info']['url_ori']
        info_list.append(info)
    result.info_list = info_list
    return result


def get_user_info(id: str) -> SpiderWeiboUserInfoVO:
    params = {
        'containerid': f'100505{str(id)}',
    }
    js = _get_json(params)
    if not js['ok']:
        raise GeneralException('gg')
    result = js['data']
    user_info = SpiderWeiboUserInfoVO()
    user_info.user_id = result['userInfo']['id']
    user_info.user_nickname = result['userInfo']['screen_name']
    user_info.user_weibo_count = result['userInfo']['statuses_count']
    user_info.is_verified = result['userInfo']['verified']
    user_info.user_description = result['userInfo']['description']
    user_info.is_male = result['userInfo']['gender'] == 'm'
    user_info.fans_count = result['userInfo']['followers_count']
    user_info.follow_count = result['userInfo']['follow_count']
    return user_info


def get_image_list(keyword: str, page_num: int) -> SpiderWeiboInfoListVO:
    # type：图片=63
    type = 63
    params = {
        'containerid': f'100103type={str(type)}&q={keyword}&t=0',
        'page_type': 'searchall',
        'page': page_num
    }
    js = _get_json(params)
    if not js['ok']:
        raise GeneralException('gg')
    result = SpiderWeiboInfoListVO()
    result.total_count = js['data']['cardlistInfo']['total']
    cards = js['data']['cards'][0]['card_group']
    image_info_list = []
    for card in cards:
        if card['card_type'] == 59:
            if card['left_element']['card_type'] == 9:
                image_info_list.append(card['left_element'])
            if card['right_element']['card_type'] == 9:
                image_info_list.append(card['right_element'])
    info_list = []
    for image_info in image_info_list:
        if 'page_info' not in image_info['mblog']:
            continue
        info = SpiderWeiboImageInfoVO()
        info.mid = image_info['mblog']['mid']
        info.content_text = image_info['mblog']['text']
        info.source_name = image_info['mblog']['source']
        info.image_url_list = list(
            map(lambda x: f"http://wx2.sinaimg.cn/large/{x}.jpg", image_info['mblog']['pic_ids']))
        info.cover_url = image_info['mblog']['thumbnail_pic']
        info.forward_count = image_info['mblog']['reposts_count']
        info.comments_count = image_info['mblog']['comments_count']
        info.liked_count = image_info['mblog']['attitudes_count']
        info.watch_later_count = image_info['mblog']['pending_approval_count']
        user_info = SpiderWeiboUserInfoVO()
        user_info.user_id = image_info['mblog']['user']['id']
        user_info.user_nickname = image_info['mblog']['user']['screen_name']
        user_info.location = image_info['mblog']['user']['location']
        user_info.user_profile_url = f"https://weibo.com/u/{image_info['mblog']['user']['profile_url']}?is_all=1"
        user_info.is_male = image_info['mblog']['user']['gender'] == 'm'
        user_info.fans_count = image_info['mblog']['user']['followers_count']
        user_info.follow_count = image_info['mblog']['user']['friends_count']
        user_info.user_weibo_count = image_info['mblog']['user']['statuses_count']
        user_info.user_video_weibo_count = image_info['mblog']['user'].get('video_statuses_count', 0)
        user_info.is_verified = image_info['mblog']['user']['verified']
        user_info.user_description = image_info['mblog']['user']['description']
        info.user_info = user_info
        info_list.append(info)
    result.info_list = info_list
    return result


def get_user_follows_and_fans(id: str, max: int = 1000) -> SpiderWeiboUserRelationshipVO:
    user_relationship = SpiderWeiboUserRelationshipVO()
    user_relationship.fan_ids = list(_get_full_fans_list_ids_by_max(id, max))
    user_relationship.follower_ids = list(_get_full_followers_list_ids_by_max(id, max))
    return user_relationship


if __name__ == '__main__':
    result = get_user_follows_and_fans('5353985393')
    follower_ids = set(result.follower_ids)
    fan_ids = set(result.fan_ids)
    print(list(follower_ids.intersection(fan_ids)))
    print(result.json(indent=4, ensure_ascii=False))
