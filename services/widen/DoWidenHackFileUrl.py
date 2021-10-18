import time

import requests
from retrying import retry

from mapper.DbVmsProd import DbVmsProd
from mapper.DbVmsUat import DbVmsUat
from services.widen import SpiderWidenService
from utils.EventLoopManagerUtils import event_loop_manager

url_goto_page = f"https://shiseido.widencollective.com/dam/searchresults.instantsearch.instantsearchpager:gotopage?newPageNum=%s"
url_update_search = "https://shiseido.widencollective.com/dam/searchresults.instantsearch.instantsearchpager:updatesearch"
url_get_download = "https://shiseido.widencollective.com/api/rest/conversion/downloads/uuid/%s"
url_get_order = "https://shiseido.widencollective.com/api/rest/conversion/order/uuid/%s?version=%s"
url_get_finally = "https://shiseido.widencollective.com/api/rest/conversion/download/uuid/%s?order=%s"
url_get_version = "https://shiseido.widencollective.com/dam/searchresults.instantsearch:getdata?start=0&end=500"




@retry(stop_max_attempt_number=3)
def _do_request(method, url, headers=None, data=None):
    response = requests.request(method, url, headers=headers, data=data)
    assert response.status_code == 200
    return response


def call_tezign(prod_token, uat_token):
    url = f"https://vms-service.tezign.com/transfer/script/shiseido?prodToken={prod_token}"

    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'x-lang': 'zh-CN',
        'X-Token': uat_token,
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        'X-User-Id': '1',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'x-tenant-id': 't16'
    }

    response = requests.request("POST", url, headers=headers, data={})
    if response.status_code != 200:
        print(response.text)


def get_fking_urls(prod_token, uat_token):
    headers = {
        'authority': 'shiseido.widencollective.com',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'x-prototype-version': '1.7',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://shiseido.widencollective.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://shiseido.widencollective.com/dam/searchresults',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': event_loop_manager.run_until_complete(
        SpiderWidenService.login_by_url_and_get_cookie('https://shiseido.widencollective.com', 'zongyang@tezign.com', 'Zst123456'))
    }
    with DbVmsUat() as db_vms_uat:
        db_vms_uat.cursor.execute(
            f"select file_name from t16.shiseido_widencollective_transfer")
        file_name_set = set(map(lambda x: x['file_name'], db_vms_uat.cursor.fetchall()))
        db_vms_uat.cursor.execute(
            f"select file_name from t16.shiseido_widencollective_transfer_record where !isnull(url)")
        file_name_set_2 = set(map(lambda x: x['file_name'], db_vms_uat.cursor.fetchall()))
    for page in range(1, 21):
        print(f"现在开始搞第{page}页...")
        # goto_page
        response = _do_request("POST", url_goto_page % page, headers=headers)
        # get_update_search
        time.sleep(0.5)
        payload = 't%3Azoneid=instantSearchZone'
        response = _do_request("POST", url_update_search, headers=headers, data=payload)
        time.sleep(0.5)
        response_uuids = response.json()['inits'][2]['InstantSearch'][0]['allUuids']
        # get_version
        response = _do_request("GET", url_get_version, headers=headers)
        response_version = response.json()

        for i, asset in enumerate(response_version['assets']):
            file_name = asset['filename']
            if not asset['canDownload']:
                continue
            if file_name in file_name_set or file_name in file_name_set_2:
                continue
            print(f"现在开始搞第{i + 1}个素材，素材名「{file_name}」...")
            file_version = asset['defaultVersionUuid']
            # get_true_uuid
            uuid = response_uuids[i]
            response = _do_request("GET", url_get_download % uuid, headers=headers)
            true_uuid = list(filter(lambda x: x['key'] == 'original-file', response.json()))[0]['uuid']
            time.sleep(0.5)
            # get_order_id
            response = _do_request("POST", url_get_order % (true_uuid, file_version), headers=headers).json()
            if response['error']:
                continue
            order_uuid = response['orderUuid']
            # get_final_url
            time.sleep(1)
            response = _do_request("GET", url_get_finally % (true_uuid, order_uuid), headers=headers).json()
            time.sleep(0.5)
            final_url = 'https://shiseido.widencollective.com' + response['url']
            # query
            with DbVmsUat() as db_vms_uat:
                db_vms_uat.cursor.execute(
                    f"insert into t16.shiseido_widencollective_transfer_record(file_name, url) values ('{file_name}', '{final_url}')")

            if i % 10 == 0:
                call_tezign(prod_token, uat_token)
            # print(f'搞好了「{file_name}」')


def wash_dirty_data():
    with DbVmsUat() as db_vms_uat:
        # db_vms_uat.cursor.execute("select asset_id from t16.shiseido_widencollective_transfer where !isnull(asset_id)")
        # asset_id_list = list(map(lambda x: str(x['asset_id']), db_vms_uat.cursor.fetchall()))
        # db_vms_prod.cursor.execute(
        #     f"select id from t248.tbl_asset where size <= 312 and id in  ({','.join(asset_id_list)})")
        # asset_id_list = list(map(lambda x: str(x['id']), db_vms_prod.cursor.fetchall()))
        # print(asset_id_list)
        # if asset_id_list:
        #     db_vms_uat.cursor.execute(
        #         f"delete from t16.shiseido_widencollective_transfer where asset_id in ({','.join(asset_id_list)})")
        db_vms_uat.cursor.execute(
                f"truncate table t16.shiseido_widencollective_transfer_record")


if __name__ == '__main__':
    # wash_dirty_data()
    get_fking_urls('04fdfa0fe23c30601c06d5bdbaf7d0ee', '5f28445dbf59e017a1fd0870a2ca7864')
    # call_tezign('04fdfa0fe23c30601c06d5bdbaf7d0ee', '5f28445dbf59e017a1fd0870a2ca7864')
