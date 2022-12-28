from pyppeteer.errors import PageError
from pyppeteer.page import Page

from utils.BrowserManager import browser_manager


class BrowserPage():
    def __init__(self, url, headers: dict = None, cookies: dict = None, mobile_mode=False, response_func: list=None, timeout=0, is_enable_js=True, smart_wait=False):
        self.browser_manager = browser_manager
        self.url = url
        self.mobile_mode = mobile_mode
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.response_func = response_func
        self.timeout = timeout
        self.is_enable_js = is_enable_js
        self.smart_wait = smart_wait

    # 进入with语句自动执行
    async def __aenter__(self) -> Page:
        self.page = await self.browser_manager.get_new_page(mobile_mode=self.mobile_mode)
        for k, v in self.cookies.items():
            await self.page.setCookie({"name": k, "value": v, "url": self.url})
        if self.response_func:
            for func in self.response_func:
                self.page.on("response", func)
        events = ['load']
        if self.smart_wait:
            events.append('networkidle0')
        await self.page.setJavaScriptEnabled(self.is_enable_js)
        await self.page.goto(self.url, timeout=self.timeout, waitUntil=events)
        return self.page



    # 退出with语句块自动执行
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser_manager.close_page(self.page)

    def __enter__(self):
        raise ValueError('wrong usage of BrowserPage! please use "async with" instead of "with".')

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise ValueError('wrong usage of BrowserPage! please use "async with" instead of "with".')
