# task_base.py
# CHANGES: 新增统一后台任务基类，提供 start/stop/cancel 约定与日志
# 目的：所有任务继承此类以保证生命周期一致性和可取消性
import asyncio
import logging
from typing import Optional

_logger = logging.getLogger("task_base")


class TaskBase:
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self._task: Optional[asyncio.Task] = None
        self._running = False

    def is_running(self) -> bool:
        return self._running and self._task is not None and not self._task.done()

    def start(self) -> asyncio.Task:
        """Start the background task. Returns asyncio.Task created."""
        if self._task and not self._task.done():
            _logger.debug("%s already started", self.name)
            return self._task
        self._running = True
        self._task = asyncio.create_task(self._run_wrapper(), name=self.name)
        return self._task

    async def stop(self, timeout: float = 5.0):
        """Stop the background task gracefully. Awaitable."""
        _logger.debug("%s stopping...", self.name)
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=timeout)
            except asyncio.CancelledError:
                _logger.debug("%s cancelled", self.name)
            except asyncio.TimeoutError:
                _logger.warning("%s stop timeout, task still running", self.name)
            finally:
                self._task = None
        _logger.debug("%s stopped", self.name)

    async def _run_wrapper(self):
        try:
            await self.run()
        except asyncio.CancelledError:
            _logger.debug("%s run cancelled", self.name)
            raise
        except Exception:
            _logger.exception("%s unexpected exception in run()", self.name)

    async def run(self):
        """Override this with the actual task coroutine."""
        raise NotImplementedError
