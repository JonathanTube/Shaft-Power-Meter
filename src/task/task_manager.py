import asyncio
import logging


class TaskManager:
    def __init__(self):
        self._tasks = []

    def add(self, t):
        self._tasks.append(t)

    async def stop_all(self):
        for t in reversed(self._tasks):
            try:
                # 如果是 asyncio.Task
                if isinstance(t, asyncio.Task):
                    t.cancel()
                    try:
                        await t
                    except asyncio.CancelledError:
                        pass
                    continue

                # 如果有 stop 方法
                stop_fn = getattr(t, "stop", None)
                if callable(stop_fn):
                    res = stop_fn()
                    if asyncio.iscoroutine(res):
                        await res
                    continue

            except Exception:
                logging.exception("TaskManager stop_all error for %s", t)
