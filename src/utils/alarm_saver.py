import asyncio
import logging
import uuid
from peewee import fn
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from common.global_data import gdata
from task.plc_sync_task import plc


class AlarmSaver:
    # 新增：全局锁对象
    _lock = asyncio.Lock()

    @staticmethod
    async def create(alarm_type: AlarmType, out_of_sync: bool = False):
        # 加锁（使用with语句确保锁自动释放）
        async with AlarmSaver._lock:
            if await asyncio.to_thread(AlarmSaver.has_alarm, alarm_type):
                return

            try:
                await asyncio.to_thread(
                    AlarmLog.create,
                    alarm_uuid=uuid.uuid4().hex,
                    alarm_type=alarm_type,
                    occured_time=gdata.configDateTime.utc,
                    out_of_sync=out_of_sync
                )

                gdata.configAlarm.set_default_value()
                await plc.write_common_alarm(True)

                logging.info(f'[创建alarm] {alarm_type}')

            except Exception as e:
                logging.exception(f'[创建alarm] 异常{e}')

    @staticmethod
    async def recovery(alarm_type: AlarmType):
        async with AlarmSaver._lock:
            try:
                has_alarm = await asyncio.to_thread(AlarmSaver.has_alarm, alarm_type)
                if has_alarm:
                    # update 也放线程池
                    await asyncio.to_thread(
                        lambda: AlarmLog.update(
                            recovery_time=gdata.configDateTime.utc,
                            is_synced=False
                        ).where(AlarmLog.alarm_type == alarm_type).execute()
                    )
                    gdata.configAlarm.set_default_value()
                    logging.info(f'[恢复alarm] {alarm_type}')

                has_alarm = await asyncio.to_thread(AlarmSaver.has_alarm, alarm_type)
                if not has_alarm:
                    await plc.write_common_alarm(False)

            except Exception as e:
                logging.exception(f'[恢复alarm] 异常{e}')

    @staticmethod
    def has_alarm(alarm_type: AlarmType) -> bool:
        cnt = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(
            AlarmLog.alarm_type == alarm_type,
            AlarmLog.recovery_time.is_null()
        ).scalar()
        return cnt > 0
