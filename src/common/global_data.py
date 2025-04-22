from datetime import datetime
from typing import Literal
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from db.models.date_time_conf import DateTimeConf


class GlobalData:
    def __init__(self):
        self.utc_date_time: datetime = None
        self.system_date_time: datetime = None

        # 是否开启shapoli功能
        systemSettings: SystemSettings = SystemSettings.get()
        self.enable_shapoli = systemSettings.sha_po_li
        # 螺旋桨数量
        self.amount_of_propeller = systemSettings.amount_of_propeller
        # 是否开启功率过载告警
        propellerSetting: PropellerSetting = PropellerSetting.get()
        self.enable_power_overload_alarm = propellerSetting.alarm_enabled_of_overload_curve
        #  是否开启自动从GPS同步UTC时间
        dateTimeConf: DateTimeConf = DateTimeConf.get()
        self.enable_utc_time_sync_with_gps = dateTimeConf.sync_with_gps

        io_conf: IOConf = IOConf.get()
        self.gps_ip = io_conf.gps_ip
        self.gps_port = io_conf.gps_port

        self.modbus_ip = io_conf.modbus_ip
        self.modbus_port = io_conf.modbus_port

        self.plc_ip = io_conf.plc_ip
        self.plc_port = io_conf.plc_port

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
        self.gps_location = None

        self.sps1_manually_start_time: datetime | None = None
        self.sps2_manually_start_time: datetime | None = None
        self.sps1_manually_status: Literal['running', 'stopped', 'reset'] = 'stopped'
        self.sps2_manually_status: Literal['running', 'stopped', 'reset'] = 'stopped'


gdata: GlobalData = GlobalData()
