import asyncio
from datetime import datetime, timedelta
import logging
from peewee import DoesNotExist
from db.models.date_time_conf import DateTimeConf
from common.global_data import gdata

class UtcTimer:
    def __init__(self):
        self.task_running = False
        self._write_interval = 60  # 每 60 秒写一次数据库
        self._last_write_time = None

    async def start(self):
        try:
            date_time_conf = DateTimeConf.get()
        except DoesNotExist:
            # 如果记录不存在，新建一条
            date_time_conf = DateTimeConf.create(
                utc_date_time=datetime.utcnow(),
                system_date_time=datetime.now()
            )

        gdata.configDateTime.utc = date_time_conf.utc_date_time
        self.task_running = True
        self._last_write_time = datetime.now()

        while self.task_running:
            try:
                # 更新内存时间
                gdata.configDateTime.utc += timedelta(seconds=1)
                gdata.configDateTime.system = datetime.now()

                # 每隔 N 秒写一次数据库
                if (datetime.now() - self._last_write_time).total_seconds() >= self._write_interval:
                    await asyncio.to_thread(
                        DateTimeConf.update(
                            utc_date_time=gdata.configDateTime.utc,
                            system_date_time=gdata.configDateTime.system
                        ).where(DateTimeConf.id == date_time_conf.id).execute
                    )
                    self._last_write_time = datetime.now()

            except asyncio.CancelledError:
                break
            except Exception:
                logging.exception('exception occurred at UtcTimer.start')

            await asyncio.sleep(1)

    def stop(self):
        self.task_running = False

utc_timer = UtcTimer()
