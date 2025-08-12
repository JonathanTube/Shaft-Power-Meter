# task/utc_timer_task.py
import asyncio
import logging
from datetime import datetime, timedelta
from db.models.date_time_conf import DateTimeConf
from common.global_data import gdata


class UtcTimerTask:
    def __init__(self):
        self.task_running = False
        self._task = None

    async def start(self):
        """启动UTC计时器"""
        if self.task_running:
            return
        self.task_running = True
        self._task = asyncio.create_task(self._run_loop())

    async def _run_loop(self):
        try:
            # 初始化读取一次配置
            date_time_conf: DateTimeConf = await asyncio.to_thread(DateTimeConf.get)
            gdata.configDateTime.utc = date_time_conf.utc_date_time

            while self.task_running:
                try:
                    if gdata.configDateTime.utc is None:
                        continue
                    # UTC时间 +1秒
                    gdata.configDateTime.utc = gdata.configDateTime.utc + timedelta(seconds=1)
                    gdata.configDateTime.system = datetime.now()

                    # 更新数据库（放到线程池执行，防止阻塞UI）
                    await asyncio.to_thread(
                        DateTimeConf.update(
                            utc_date_time=gdata.configDateTime.utc,
                            system_date_time=gdata.configDateTime.system
                        ).where(DateTimeConf.id == date_time_conf.id).execute
                    )
                except Exception:
                    logging.exception("UtcTimerTask 循环异常")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def stop(self):
        self.task_running = False
        if self._task and not self._task.done():
            try:
                self._task.cancel()
                await asyncio.sleep(0)  # 给任务调度机会
            except asyncio.CancelledError:
                pass
        self._task = None


utc_timer = UtcTimerTask()
