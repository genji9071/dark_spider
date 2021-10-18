import asyncio
import threading

_lock = threading.RLock()


def lock(func):
    def wrapper(*args, **kwargs):
        _lock.acquire()
        try:
            return func(*args, **kwargs)
        finally:
            _lock.release()

    return wrapper


class EventLoopManager():
    def __init__(self):
        self.loop = asyncio.new_event_loop()

    @lock
    def run_until_complete(self, item):
        return self.loop.run_until_complete(item)


event_loop_manager = EventLoopManager()
