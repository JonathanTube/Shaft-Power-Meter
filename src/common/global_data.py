from datetime import datetime
from db.models.factor_conf import FactorConf
from db.models.offline_default_value import OfflineDefaultValue
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from db.models.date_time_conf import DateTimeConf
from db.models.zero_cal_info import ZeroCalInfo


class GlobalData:
    def __init__(self):
        self.is_master = False

        self.auto_testing = False

        self.default_table_width = 990
        self.utc_date_time: datetime = None
        self.system_date_time: datetime = None

        self.shapoli = False

        self.amount_of_propeller = 1

        self.eexi_breach_checking_duration = 5

        self.eexi_limited_power = 999999

        #  是否开启自动从GPS同步UTC时间
        self.enable_utc_time_sync_with_gps = False

        # 作为服务端, 是否已启动
        self.master_server_started = False
        # 作为客户端，是否已连接
        self.connected_to_hmi_server = False
        # modbus output服务是否已经打开
        self.modbus_server_started = False
        # 是否连上gps
        self.connected_to_gps = False

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
        self.test_mode_start_time = None

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

        # 计算参数
        self.bearing_outer_diameter_D = 0
        self.bearing_inner_diameter_d = 0
        self.elastic_modulus_E = 0
        self.poisson_ratio_mu = 0
        self.sensitivity_factor_k = 0

        self.gps_raw_data = ""

        self.alarm_enabled_of_overload_curve = False

        self.eexi_breach = False

    def set_default_value(self):
        systemSettings: SystemSettings = SystemSettings.get()

        self.is_master = systemSettings.is_master

        self.amount_of_propeller = systemSettings.amount_of_propeller

        self.shapoli = systemSettings.sha_po_li

        self.eexi_breach_checking_duration = systemSettings.eexi_breach_checking_duration
        
        self.eexi_limited_power = systemSettings.eexi_limited_power

        dateTimeConf: DateTimeConf = DateTimeConf.get()
        self.enable_utc_time_sync_with_gps = dateTimeConf.sync_with_gps

        propellerSetting: PropellerSetting = PropellerSetting.get()
        self.speed_of_mcr = propellerSetting.rpm_of_mcr_operating_point
        self.power_of_mcr = propellerSetting.shaft_power_of_mcr_operating_point
        self.speed_of_torque_load_limit = propellerSetting.rpm_right_of_torque_load_limit_curve
        self.power_of_torque_load_limit = propellerSetting.bhp_right_of_torque_load_limit_curve + \
            propellerSetting.value_of_overload_curve
        self.power_of_overload = propellerSetting.value_of_overload_curve
        self.alarm_enabled_of_overload_curve = propellerSetting.alarm_enabled_of_overload_curve
        # get the last accepted zero cal. record.
        sps1_accepted_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(
            ZeroCalInfo.state == 1, ZeroCalInfo.name == 'sps1').order_by(ZeroCalInfo.id.desc()).first()
        if sps1_accepted_zero_cal is not None:
            self.sps1_torque_offset = sps1_accepted_zero_cal.torque_offset
            self.sps1_thrust_offset = sps1_accepted_zero_cal.thrust_offset

        sps2_accepted_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(ZeroCalInfo.state == 1, ZeroCalInfo.name == 'sps2').order_by(ZeroCalInfo.id.desc()).first()
        if sps2_accepted_zero_cal is not None:
            self.sps2_torque_offset = sps2_accepted_zero_cal.torque_offset
            self.sps2_thrust_offset = sps2_accepted_zero_cal.thrust_offset

        offline_default_value: OfflineDefaultValue = OfflineDefaultValue.get()
        self.sps_offline_thrust = offline_default_value.thrust_default_value
        self.sps_offline_torque = offline_default_value.torque_default_value
        self.sps_offline_speed = offline_default_value.speed_default_value

        factor_conf: FactorConf = FactorConf.get()
        self.bearing_outer_diameter_D = factor_conf.bearing_outer_diameter_D
        self.bearing_inner_diameter_d = factor_conf.bearing_inner_diameter_d
        self.elastic_modulus_E = factor_conf.elastic_modulus_E
        self.poisson_ratio_mu = factor_conf.poisson_ratio_mu
        self.sensitivity_factor_k = factor_conf.sensitivity_factor_k


gdata: GlobalData = GlobalData()
