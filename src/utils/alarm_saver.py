import logging
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from common.global_data import gdata
from common.control_manager import ControlManager
from utils.plc_util import plc_util
import asyncio


class AlarmSaver:
    @staticmethod
    def create(alarm_type: AlarmType):
        cnt: int = AlarmLog.select().where(AlarmLog.alarm_type == alarm_type, AlarmLog.is_recovery == False).count()
        logging.info(f'[***save alarm***]alarm_type={alarm_type}, exists alarm records = {cnt}')
        if cnt == 0:
            AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=alarm_type)
            logging.info(f'[***save alarm***]alarm_type={alarm_type}, save alarm log')
            asyncio.create_task(plc_util.write_alarm(True))
        else:
            logging.info(f'[***save alarm***]alarm_type={alarm_type}, skip since record exists.')

        if ControlManager.alarm_button:
            ControlManager.alarm_button.update_alarm()

    @staticmethod
    def recovery(alarm_type: AlarmType):
        logging.info(f'[***recovery alarm***]alarm_type={alarm_type}')
        AlarmLog.update(is_recovery=True).where(AlarmLog.alarm_type == alarm_type).execute()
        # if it doesn't exist any errors. set the alarm false.
        cnt: int = AlarmLog.select().where(AlarmLog.is_recovery == False).count()
        logging.info(f'[***recovery alarm***], exists alarm records = {cnt}')
        if cnt == 0:
            logging.info(f'[***recovery alarm***], set plc alarm all to false')
            asyncio.create_task(plc_util.write_alarm(False))

        if ControlManager.alarm_button:
            ControlManager.alarm_button.update_alarm()