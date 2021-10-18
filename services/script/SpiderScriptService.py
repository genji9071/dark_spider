from utils.AsyncPool import AsyncPool
from utils.BrowserManager.BrowserPage import BrowserPage
from vo.SpiderBaseGetVideoInfoBatchResponseVO import SpiderBaseGetVideoInfoBatchResponseVO


async def get_dump_pages(pages_count: int, time_second: int) -> SpiderBaseGetVideoInfoBatchResponseVO:
    async def task():
        nonlocal success_count
        async with BrowserPage("https://www.baidu.com") as page:
            await page.waitFor(time_second * 1000)
            success_count += 1

    result = SpiderBaseGetVideoInfoBatchResponseVO()
    result.total_count = pages_count
    success_count = 0
    async with AsyncPool() as pool:
        for i in range(0, pages_count):
            pool.put(task)
    result.success_count = success_count
    return result
