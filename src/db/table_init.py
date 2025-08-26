import logging
from common.const_alarm_type import AlarmType
from db.models.breach_reason import BreachReason
from db.models.counter_log import CounterLog
from db.models.data_log import DataLog
from db.models.date_time_conf import DateTimeConf
from db.models.event_log import EventLog
from db.models.factor_conf import FactorConf
from db.models.gps_log import GpsLog
from db.models.io_conf import IOConf
from db.models.limitations import Limitations
from db.models.operation_log import OperationLog
from db.models.offline_default_value import OfflineDefaultValue
from db.models.preference import Preference
from db.models.propeller_setting import PropellerSetting
from db.models.report_detail import ReportDetail
from db.models.report_info import ReportInfo
from db.models.ship_info import ShipInfo
from db.models.system_settings import SystemSettings
from db.models.zero_cal_info import ZeroCalInfo
from db.models.zero_cal_record import ZeroCalRecord
from db.models.language import Language
from db.models.alarm_log import AlarmLog
from db.models.test_mode_conf import TestModeConf
from db.models.user import User
from db.base import db


class TableInit:
    @staticmethod
    def init():
        # db.drop_tables([Language], safe=False)
        # db.drop_tables([DataLog], safe=False)
        # db.drop_tables([OperationLog], safe=False)
        # db.drop_tables([IOConf], safe=False)
        db.create_tables([
            BreachReason,
            DataLog,
            DateTimeConf,
            EventLog,
            FactorConf,
            GpsLog,
            IOConf,
            Limitations,
            Preference,
            PropellerSetting,
            ReportDetail,
            ReportInfo,
            ShipInfo,
            SystemSettings,
            ZeroCalInfo,
            ZeroCalRecord,
            Language,
            AlarmLog,
            TestModeConf,
            User,
            OperationLog,
            CounterLog,
            OfflineDefaultValue
        ], safe=True)

    @staticmethod
    def cleanup():
        try:
            AlarmLog.delete().where(AlarmLog.alarm_type == AlarmType.POWER_OVERLOAD).execute()
            CounterLog.update(sum_speed=0, sum_power=0, times=0, seconds=0).where(CounterLog.sps_name == 'sps').execute()
            CounterLog.update(sum_speed=0, sum_power=0, times=0, seconds=0).where(CounterLog.sps_name == 'sps2').execute()
            DataLog.truncate_table()
            DateTimeConf.truncate_table()
            EventLog.truncate_table()
            GpsLog.truncate_table()
            OperationLog.truncate_table()
            ReportDetail.truncate_table()
            ReportInfo.truncate_table()
            ZeroCalInfo.truncate_table()
            ZeroCalRecord.truncate_table()
        except Exception:
            logging.exception("清理失败")
