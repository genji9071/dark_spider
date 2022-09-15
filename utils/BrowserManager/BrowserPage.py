from pyppeteer.errors import PageError
from pyppeteer.page import Page

from utils.BrowserManager import browser_manager


class BrowserPage():
    def __init__(self, url, headers: dict = None, cookies: dict = None, mobile_mode=False, response_func: list=None, timeout=30):
        self.browser_manager = browser_manager
        self.url = url
        self.mobile_mode = mobile_mode
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.response_func = response_func
        self.timeout = timeout

    # 进入with语句自动执行
    async def __aenter__(self) -> Page:
        try:
            self.page = await self.browser_manager.get_new_page(mobile_mode=self.mobile_mode)
            for k, v in self.cookies.items():
                await self.page.setCookie({"name": k, "value": v, "url": self.url})
            if self.response_func:
                for func in self.response_func:
                    self.page.on("response", func)

            await self.page.goto(self.url, timeout=self.timeout)
            return self.page
        finally:
            if self.page:
                try:
                    await self.browser_manager.close_page(self.page)
                except PageError:
                    pass



    # 退出with语句块自动执行
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser_manager.close_page(self.page)

    def __enter__(self):
        raise ValueError('wrong usage of BrowserPage! please use "async with" instead of "with".')

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise ValueError('wrong usage of BrowserPage! please use "async with" instead of "with".')
