from datetime import datetime
from typing import Literal
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from db.models.date_time_conf import DateTimeConf


class GlobalData:
    def __init__(self):
        self.default_table_width = 990
        self.utc_date_time: datetime = None
        self.system_date_time: datetime = None

        # 是否开启shapoli功能
        self.enable_shapoli = False
        # 螺旋桨数量
        self.amount_of_propeller = 1
        # 是否开启功率过载告警
        self.enable_power_overload_alarm = False
        #  是否开启自动从GPS同步UTC时间
        self.enable_utc_time_sync_with_gps = False

        self.gps_ip = None
        self.gps_port = None

        self.sps1_ip = None
        self.sps1_port = None

        self.sps2_ip = None
        self.sps2_port = None

        self.plc_ip = None
        self.plc_port = None

        self.sps1_speed = 0
        self.sps1_power = 0
        self.sps1_torque = 0
        self.sps1_thrust = 0
        self.sps1_rounds = 0

        self.sps2_speed = 0
        self.sps2_power = 0
        self.sps2_torque = 0
        self.sps2_thrust = 0
        self.sps2_rounds = 0

        self.sps1_power_history: list[float, datetime] = []
        self.sps2_power_history: list[float, datetime] = []
        self.gps_location = None

        self.sps1_manually_start_time: datetime | None = None
        self.sps2_manually_start_time: datetime | None = None
        self.sps1_manually_status: Literal['running', 'stopped', 'reset'] = 'stopped'
        self.sps2_manually_status: Literal['running', 'stopped', 'reset'] = 'stopped'

        self.test_mode_running: bool = False

    def set_default_value(self):
        systemSettings: SystemSettings = SystemSettings.get()
        self.enable_shapoli = systemSettings.sha_po_li
        self.amount_of_propeller = systemSettings.amount_of_propeller
        self.display_propeller_curve = systemSettings.display_propeller_curve


        propellerSetting: PropellerSetting = PropellerSetting.get()
        self.enable_power_overload_alarm = propellerSetting.alarm_enabled_of_overload_curve

        dateTimeConf: DateTimeConf = DateTimeConf.get()
        self.enable_utc_time_sync_with_gps = dateTimeConf.sync_with_gps

        io_conf: IOConf = IOConf.get()
        self.gps_ip = io_conf.gps_ip
        self.gps_port = io_conf.gps_port

        self.sps1_ip = io_conf.sps1_ip
        self.sps1_port = io_conf.sps1_port

        self.sps2_ip = io_conf.sps2_ip
        self.sps2_port = io_conf.sps2_port

        self.plc_ip = io_conf.plc_ip
        self.plc_port = io_conf.plc_port


gdata: GlobalData = GlobalData()
