from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from common.global_data import gdata
from common.control_manager import ControlManager
from utils.plc_util import plc_util
import asyncio


class AlarmSaver:
    @staticmethod
    def create(alarm_type: AlarmType):
        cnt: int = AlarmLog.select().where(AlarmLog.alarm_type == alarm_type, AlarmLog.acknowledge_time.is_null()).count()
        if cnt == 0:
            AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=alarm_type)
            asyncio.create_task(plc_util.write_alarm(True))

        if ControlManager.alarm_button:
            ControlManager.alarm_button.update_alarm()

    @staticmethod
    def acknowledge(data: list[AlarmLog]):
        for row in data:
            AlarmLog.update(acknowledge_time=gdata.utc_date_time).where(AlarmLog.id == row.id).execute()

        if ControlManager.alarm_button:
            ControlManager.alarm_button.update_alarm()
