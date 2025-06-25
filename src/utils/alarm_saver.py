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
            AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=alarm_type)
            logging.info(f'[***save alarm***] alarm_type={alarm_type}, save alarm log')

    @staticmethod
    def recovery(alarm_type: AlarmType):
        logging.info(f'[***recovery alarm***] alarm_type={alarm_type}')
        AlarmLog.update(
            is_recovery=True, 
            is_sync=False
        ).where(
            AlarmLog.alarm_type == alarm_type,
            AlarmLog.is_recovery == False
        ).execute()