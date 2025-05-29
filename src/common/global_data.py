from datetime import datetime
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from db.models.date_time_conf import DateTimeConf


class GlobalData:
    def __init__(self):
        self.default_table_width = 980
        self.utc_date_time: datetime = None
        self.system_date_time: datetime = None

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
        self.write_real_time_data_to_plc = False

        self.sps1_speed = 0
        self.sps1_power = 0
        self.sps1_torque = 0
        self.sps1_torque_mv_per_v = 0
        self.sps1_thrust = 0
        self.sps1_thrust_mv_per_v = 0

        self.sps2_speed = 0
        self.sps2_power = 0
        self.sps2_torque = 0
        self.sps2_torque_mv_per_v = 0
        self.sps2_thrust = 0
        self.sps2_thrust_mv_per_v = 0

        self.sps1_power_history: list[float, datetime] = []
        self.sps2_power_history: list[float, datetime] = []
        self.gps_location = None

        self.test_mode_running: bool = False

        self.speed_of_mcr = 0
        self.power_of_mcr = 0
        self.speed_of_torque_load_limit = 0
        self.power_of_torque_load_limit = 0
        self.power_of_overload = 0

    def set_default_value(self):
        systemSettings: SystemSettings = SystemSettings.get()
        self.display_propeller_curve = systemSettings.display_propeller_curve

        dateTimeConf: DateTimeConf = DateTimeConf.get()
        self.enable_utc_time_sync_with_gps = dateTimeConf.sync_with_gps

        io_conf: IOConf = IOConf.get()
        self.gps_ip = io_conf.gps_ip
        self.gps_port = io_conf.gps_port
        self.write_real_time_data_to_plc = io_conf.write_real_time_data_to_plc

        self.sps1_ip = io_conf.sps1_ip
        self.sps1_port = io_conf.sps1_port

        self.sps2_ip = io_conf.sps2_ip
        self.sps2_port = io_conf.sps2_port

        self.plc_ip = io_conf.plc_ip
        self.plc_port = io_conf.plc_port

        propellerSetting: PropellerSetting = PropellerSetting.get()
        self.speed_of_mcr = propellerSetting.rpm_of_mcr_operating_point
        self.power_of_mcr = propellerSetting.shaft_power_of_mcr_operating_point
        self.speed_of_torque_load_limit = propellerSetting.rpm_right_of_torque_load_limit_curve
        self.power_of_torque_load_limit = propellerSetting.bhp_right_of_torque_load_limit_curve + propellerSetting.value_of_overload_curve
        self.power_of_overload = propellerSetting.value_of_overload_curve


gdata: GlobalData = GlobalData()
