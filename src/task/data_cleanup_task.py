# task/data_cleanup_task.py
# 说明：定期清理历史数据（例如 3 个月之前），单独任务统一 start/stop

import asyncio
import logging
from datetime import timedelta
from db.models.data_log import DataLog
from common.global_data import gdata

logger = logging.getLogger("DataCleanupTask")


class DataCleanupTask:
    def __init__(self, weeks_keep: int = 12):
        self._task = None
        self._running = False
        self.weeks_keep = weeks_keep

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop(), name="data-cleanup")

    async def _loop(self):
        try:
            while self._running:
                try:
                    utc_now = getattr(gdata.configDateTime, "utc", None)
                    if utc_now:
                        cutoff = utc_now - timedelta(weeks=self.weeks_keep)
                        # 删除旧记录（放在线程池）
                        await asyncio.to_thread(DataLog.delete().where(DataLog.utc_date_time < cutoff).execute)
                        logger.info("DataCleanupTask 已清理旧数据")
                except Exception:
                    logger.exception("DataCleanupTask 清理异常")
                # 每小时检查一次（可改）
                await asyncio.sleep(60 * 60)
        finally:
            self._running = False

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


data_cleanup_task = DataCleanupTask()