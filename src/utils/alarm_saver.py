import logging
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from common.global_data import gdata
from task.plc_sync_task import plc
import asyncio


class AlarmSaver:
    @staticmethod
    def create(alarm_type: AlarmType):
        cnt: int = AlarmLog.select().where(
                        AlarmLog.alarm_type == alarm_type, 
                        AlarmLog.is_recovery == False
                    ).count()
        logging.info(f'[***save alarm***] alarm_type={alarm_type}, exists alarm records = {cnt}')
        if cnt == 0:
            AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=alarm_type)
            logging.info(f'[***save alarm***] alarm_type={alarm_type}, save alarm log')
            asyncio.create_task(plc.write_alarm(True))

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

        # if it doesn't exist any errors. set the alarm false.
        cnt: int = AlarmLog.select().where(AlarmLog.is_recovery == False).count()
        logging.info(f'[***recovery alarm***], exists alarm records = {cnt}, skip clear plc alarm.')

        if cnt == 0:
            logging.info(f'[***recovery alarm***], clear all plc alarm.')

            if gdata.is_master and plc.is_connected:
                asyncio.create_task(plc.write_alarm(False))
