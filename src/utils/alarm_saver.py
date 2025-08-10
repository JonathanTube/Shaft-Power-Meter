import logging
import threading
from peewee import fn, Case
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
            cnt_occured, cnt_recovery = AlarmSaver.get_cnts(alarm_type)
            # 报警发生数量大于恢复数量，无需再添加报警记录
            if cnt_occured > cnt_recovery:
                return
            AlarmLog.create(
                utc_date_time=gdata.configDateTime.utc,
                alarm_type=alarm_type,
                is_recovery=False,
                is_from_master=gdata.configCommon.is_master
            )
            logging.info(f'[***save alarm***] alarm_type={alarm_type}, save alarm log')

    @staticmethod
    def recovery(alarm_type: AlarmType):
        with AlarmSaver._lock:
            cnt_occured, cnt_recovery = AlarmSaver.get_cnts(alarm_type)
            # 如果报警数量大于恢复数量，则需要恢复
            if cnt_occured > cnt_recovery:
                AlarmLog.create(
                    utc_date_time=gdata.configDateTime.utc,
                    alarm_type=alarm_type,
                    is_recovery=True,
                    is_from_master=gdata.configCommon.is_master
                )

    @staticmethod
    def get_cnts(alarm_type: AlarmType) -> tuple[int, int]:
        cnts = (
            AlarmLog.select(
                fn.COUNT(Case(None, [(AlarmLog.is_recovery == False, 1)])).alias('cnt_occured'),
                fn.COUNT(Case(None, [(AlarmLog.is_recovery == True, 1)])).alias('cnt_recovery')
            )
            .where(AlarmLog.alarm_type == alarm_type).dicts().get()
        )

        return cnts['cnt_occured'], cnts['cnt_recovery']
