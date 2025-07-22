import logging
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from common.global_data import gdata


class AlarmSaver:
    @staticmethod
    def create(alarm_type: AlarmType):
        cnt: int = AlarmLog.select().where(
            AlarmLog.alarm_type == alarm_type,
            AlarmLog.is_recovery == False
        ).count()
        if cnt == 0:
            AlarmLog.create(utc_date_time=gdata.utc_date_time,
                            alarm_type=alarm_type,
                            is_from_master=gdata.is_master)
            logging.info(f'[***save alarm***] alarm_type={alarm_type}, save alarm log')

    @staticmethod
    def recovery(alarm_type_occured: AlarmType, alarm_type_recovered: AlarmType):
        cnt: int = AlarmLog.select().where(
            AlarmLog.alarm_type == alarm_type_occured,
            AlarmLog.is_recovery == False
        ).count()
        # 如何过没待恢复的记录，直接跳过
        if cnt == 0:
            return
        
        AlarmLog.update(
            is_recovery=True,
            is_sync=False
        ).where(
            AlarmLog.alarm_type == alarm_type_occured,
            AlarmLog.is_recovery == False,
            AlarmLog.is_from_master == gdata.is_master
        ).execute()

        AlarmLog.create(utc_date_time=gdata.utc_date_time,
                        alarm_type=alarm_type_recovered,
                        is_recovery=True,
                        is_from_master=gdata.is_master)
