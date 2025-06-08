from datetime import datetime
from db.models.io_conf import IOConf
from db.models.offline_default_value import OfflineDefaultValue
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from db.models.date_time_conf import DateTimeConf
from db.models.zero_cal_info import ZeroCalInfo


class GlobalData:
    def __init__(self):
        self.default_table_width = 1010
        self.utc_date_time: datetime = None
        self.system_date_time: datetime = None

        self.amount_of_propeller = 1

        #  是否开启自动从GPS同步UTC时间
        self.enable_utc_time_sync_with_gps = False

        # 作为服务端, 是否已启动
        self.hmi_server_started = False
        # 作为客户端，是否已连接
        self.connected_to_hmi_server = False
        # modbus output服务是否已经打开
        self.modbus_server_started = False

        self.gps_ip = None
        self.gps_port = None

        self.sps1_ip = None
        self.sps1_port = None

        self.sps2_ip = None
        self.sps2_port = None

        self.plc_enabled = False
        self.plc_ip = None
        self.plc_port = None

        self.sps1_speed = 0
        self.sps1_power = 0
        self.sps1_torque = 0
        self.sps1_thrust = 0
        
        self.sps1_ad0 = 0
        self.sps1_ad1 = 0
        self.sps1_speed = 0

        self.sps1_mv_per_v_for_torque = 0
        self.sps1_mv_per_v_for_thrust = 0
        self.sps1_torque_offset = 0
        self.sps1_thrust_offset = 0

        self.sps2_speed = 0
        self.sps2_power = 0
        self.sps2_torque = 0
        self.sps2_thrust = 0

        self.sps2_ad0 = 0
        self.sps2_ad1 = 0
        self.sps2_speed = 0

        self.sps2_mv_per_v_for_torque = 0
        self.sps2_mv_per_v_for_thrust = 0
        self.sps2_torque_offset = 0
        self.sps2_thrust_offset = 0

        self.sps1_power_history: list[float, datetime] = []
        self.sps2_power_history: list[float, datetime] = []
        self.gps_location = None

        self.test_mode_running: bool = False

        self.speed_of_mcr = 0
        self.power_of_mcr = 0
        self.speed_of_torque_load_limit = 0
        self.power_of_torque_load_limit = 0
        self.power_of_overload = 0

        # 默认离线
        self.sps1_offline: bool = True
        self.sps2_offline: bool = True
        self.sps_offline_torque = 0
        self.sps_offline_thrust = 0
        self.sps_offline_speed = 0

    def set_default_value(self):
        systemSettings: SystemSettings = SystemSettings.get()
        self.display_propeller_curve = systemSettings.display_propeller_curve

        self.amount_of_propeller = systemSettings.amount_of_propeller

        dateTimeConf: DateTimeConf = DateTimeConf.get()
        self.enable_utc_time_sync_with_gps = dateTimeConf.sync_with_gps

        io_conf: IOConf = IOConf.get()
        self.gps_ip = io_conf.gps_ip
        self.gps_port = io_conf.gps_port
        self.plc_enabled = io_conf.plc_enabled

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
        self.power_of_torque_load_limit = propellerSetting.bhp_right_of_torque_load_limit_curve + \
            propellerSetting.value_of_overload_curve
        self.power_of_overload = propellerSetting.value_of_overload_curve
        # get the last accepted zero cal. record.
        sps1_accepted_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(
            ZeroCalInfo.state == 1, ZeroCalInfo.name == 'sps1').order_by(ZeroCalInfo.id.desc()).first()
        if sps1_accepted_zero_cal is not None:
            self.sps1_torque_offset = sps1_accepted_zero_cal.torque_offset
            self.sps1_thrust_offset = sps1_accepted_zero_cal.thrust_offset

        sps2_accepted_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(
            ZeroCalInfo.state == 1, ZeroCalInfo.name == 'sps2').order_by(ZeroCalInfo.id.desc()).first()
        if sps2_accepted_zero_cal is not None:
            self.sps2_torque_offset = sps2_accepted_zero_cal.torque_offset
            self.sps2_thrust_offset = sps2_accepted_zero_cal.thrust_offset

        offline_default_value: OfflineDefaultValue = OfflineDefaultValue.get()
        self.sps_offline_thrust = offline_default_value.thrust_default_value
        self.sps_offline_torque = offline_default_value.torque_default_value
        self.sps_offline_speed = offline_default_value.speed_default_value


gdata: GlobalData = GlobalData()
