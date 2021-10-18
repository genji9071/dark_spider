from pyppeteer.page import Page

from utils.BrowserManager import browser_manager


class BrowserPage():
    def __init__(self, url, headers: dict = None, cookies: dict = None, mobile_mode=False):
        self.browser_manager = browser_manager
        self.url = url
        self.mobile_mode = mobile_mode
        self.headers = headers or {}
        self.cookies = cookies or {}

    # 进入with语句自动执行
    async def __aenter__(self) -> Page:
        self.page = await self.browser_manager.get_new_page(mobile_mode=self.mobile_mode)
        for k, v in self.cookies.items():
            await self.page.setCookie({"name": k, "value": v, "url": self.url})
        await self.page.goto(self.url)
        return self.page

    # 退出with语句块自动执行
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser_manager.close_page(self.page)

    def __enter__(self):
        raise ValueError('wrong usage of BrowserPage! please use "async with" instead of "with".')

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise ValueError('wrong usage of BrowserPage! please use "async with" instead of "with".')
