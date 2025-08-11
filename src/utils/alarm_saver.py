import logging
import threading
from peewee import fn
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from common.global_data import gdata


class AlarmSaver:
    # 新增：全局锁对象
    _lock = threading.Lock()

    @staticmethod
    def create(alarm_type: AlarmType):
        # 加锁（使用with语句确保锁自动释放）
        with AlarmSaver._lock:
            if AlarmSaver.has_alarm(alarm_type):
                return

            AlarmLog.create(
                alarm_type=alarm_type,
                occured_time=gdata.configDateTime.utc,
                is_from_master=gdata.configCommon.is_master
            )
            logging.info(f'[create alarm] {alarm_type}')

    @staticmethod
    def recovery(alarm_type: AlarmType):
        with AlarmSaver._lock:
            if AlarmSaver.has_alarm(alarm_type):
                AlarmLog.update(
                    recovery_time=gdata.configDateTime.utc,
                    is_sync=False
                ).where(AlarmLog.alarm_type == alarm_type).execute()
                logging.info(f'[recovery alarm] {alarm_type}')

    @staticmethod
    def has_alarm(alarm_type: AlarmType) -> tuple[int, int]:
        cnt = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(
            AlarmLog.alarm_type == alarm_type,
            AlarmLog.recovery_time.is_null()
        ).scalar()
        return cnt > 0
