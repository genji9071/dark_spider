import asyncio
import time
from asyncio import Queue
from typing import AsyncContextManager, List, Any, Callable, Coroutine

from config import config


class AsyncPool(AsyncContextManager):
    _workers: List[Any]
    _queue: Queue

    def __init__(self, max_concurrence: int = config['browser-manager']['page_maximum_per_task']):
        self._queue = Queue()
        self._workers = []
        for i in range(max_concurrence):
            worker = asyncio.create_task(self._worker())
            self._workers.append(worker)

    def put(self, item: Callable[[], Coroutine]):
        self._queue.put_nowait(item)

    async def __aenter__(self) -> "AsyncPool":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        started_at = time.monotonic()
        await self._queue.join()
        stopped_at = time.monotonic()

        # 终止所有无限循环的worker
        for worker in self._workers:
            worker.cancel()

        # 等待cancel
        await asyncio.gather(*self._workers, return_exceptions=True)
        print('====')
        print(f'任务完毕，总共耗时{stopped_at - started_at}s。')

    async def _worker(self):
        while True:
            task = await self._queue.get()
            await task()
            self._queue.task_done()