import asyncio
import re

from exceptions.GeneralException import GeneralException
from utils.BrowserManager.BrowserPage import BrowserPage
from utils.EventLoopManagerUtils import event_loop_manager

WIDEN_URL_REGEX = r'.+.widencollective.com'


def verifyUrl(url: str):
    re_result = re.fullmatch(WIDEN_URL_REGEX, url)
    if re_result is None:
        raise GeneralException(f'verifyUrl error occurred! url: {url}')
    pass


async def login_by_url_and_get_cookie(url: str, email: str, password: str):
    async with BrowserPage(url) as page:
        await page.waitForSelector('#loginFormFieldWrapper')
        await page.type('#username', email)
        await page.type('#password', password)
        await page.click('#loginSubmit')
        await page.waitForXPath('//span[@class="Select-arrow-zone"]')
        await page.click('.Select-arrow-zone')
        await page.waitForXPath('//a[@id="react-select-3--option-0"]')
        await page.click('#react-select-3--option-0')
        await page.waitForXPath('//span[@class="Select-arrow-zone"]')
        result = ""
        cookies = await page.cookies(page.url)
        for cookie in cookies:
            result += f"{cookie['name']}={cookie['value']}; "
        return result


if __name__ == '__main__':
    print(event_loop_manager.run_until_complete(
        login_by_url_and_get_cookie('https://shiseido.widencollective.com', 'zongyang@tezign.com', 'Zst123456')))
