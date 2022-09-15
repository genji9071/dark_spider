from typing import List

from loguru import logger
from pyppeteer import launch
from pyppeteer.page import Page

from config import config
from utils.EventLoopManagerUtils import event_loop_manager
from vo.script.SpiderScriptBrowserPageInfoVO import SpiderScriptBrowserPageInfoVO


class BrowserManager():
    def __init__(self):
        self.browser_manager_config = config['browser-manager']
        event_loop_manager.run_until_complete(self.initialize())

    async def initialize(self):
        self.browser = await launch(
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            headless=self.browser_manager_config['slience'],
            devtools=not self.browser_manager_config['slience'],
            executablePath=self.browser_manager_config['chromium_path'],
            args=['--disable-infobars', '--no-sandbox'],
        )

    async def get_new_page(self, mobile_mode=False) -> Page:
        page = await self.browser.newPage()
        if mobile_mode:
            await page.setUserAgent(
                'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1')
            await page.setViewport(viewport={'width': 414, 'height': 736, 'isMobile': True, 'hasTouch': True})
        else:
            await page.setUserAgent(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36')
            await page.setViewport(viewport={'width': 1536, 'height': 768})
        await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                         '{ webdriver:{ get: () => false } }) }')
        return page

    async def close_page(self, page: Page):
        await page.close()

    async def get_browser_page_info(self) -> List[SpiderScriptBrowserPageInfoVO]:
        pages = await self.browser.pages()
        return list(map(lambda x: x.url, pages))

    async def get_page_count(self) -> int:
        page_num = len(await self.browser.pages())
        logger.info(f'current page count: {str(page_num)}')
        return page_num

    async def refresh_browser(self, force=False) -> str:
        if await self.get_page_count() > 1 and not force:
            return "尚有任务正在执行"
        page_list = await self.browser.pages()
        for page in page_list:
            await page.close(runBeforeUnload=True)
        await self.browser.close()
        await self.initialize()
        return "刷新完成"
