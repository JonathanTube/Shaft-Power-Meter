from dataclasses import dataclass, field
from datetime import datetime
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.counter_log import CounterLog
from db.models.event_log import EventLog
from db.models.factor_conf import FactorConf
from db.models.io_conf import IOConf
from db.models.limitations import Limitations
from db.models.offline_default_value import OfflineDefaultValue
from db.models.preference import Preference
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from db.models.date_time_conf import DateTimeConf
from db.models.zero_cal_info import ZeroCalInfo
from typing import Literal
from peewee import fn


@dataclass
class ConfigCommon:
    is_master = False

    is_individual = False

    enable_gps = False

    hide_admin_account = False

    amount_of_propeller = 1

    is_twins = False

    shapoli = False

    show_thrust = False

    show_propeller_curve = False

    eexi_limited_power: int = 999999
    unlimited_power: int = 999999

    eexi_breach_checking_duration: int = 5

    default_table_width: int = 990

    # 是否功率突破EEXI
    is_eexi_breaching = False

    def set_default_value(self):
        systemSettings: SystemSettings = SystemSettings.get()
        self.is_master = systemSettings.is_master
        self.enable_gps = systemSettings.enable_gps
        self.hide_admin_account = systemSettings.hide_admin_account
        self.amount_of_propeller = systemSettings.amount_of_propeller
        self.is_twins = systemSettings.amount_of_propeller > 1
        self.shapoli = systemSettings.sha_po_li
        self.eexi_breach_checking_duration = systemSettings.eexi_breach_checking_duration
        self.eexi_limited_power = systemSettings.eexi_limited_power
        self.unlimited_power = systemSettings.unlimited_power
        self.show_thrust = systemSettings.display_thrust
        self.show_propeller_curve = systemSettings.display_propeller_curve
        self.is_individual = systemSettings.is_individual


@dataclass
class ConfigAlarm:
    # 报警总数
    alarm_total_count = 0
    # 未应答数量
    alarm_not_ack = 0

    def set_default_value(self):
        # 所有告警数量
        self.alarm_total_count = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(
            AlarmLog.recovery_time.is_null()
        ).scalar()

        # 未确认告警数量
        self.alarm_not_ack = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(
            AlarmLog.acknowledge_time.is_null()
        ).scalar()


@dataclass
class ConfigPreference:
    theme = 0
    fullscreen = True
    system_unit = 0
    language = 0
    data_collection_seconds_range = 2

    def set_default_value(self):
        preference: Preference = Preference.get()
        self.theme = preference.theme
        self.fullscreen = preference.fullscreen
        self.system_unit = preference.system_unit
        self.language = preference.language
        self.data_collection_seconds_range = preference.data_collection_seconds_range


@dataclass
class ConfigLimitation:
    power_max = 0
    speed_max = 0
    torque_max = 0
    speed_warning = 0
    torque_warning = 0
    power_warning = 0

    def set_default_value(self):
        limitations: Limitations = Limitations.get()
        self.power_max = limitations.power_max
        self.speed_max = limitations.speed_max
        self.torque_max = limitations.torque_max
        self.speed_warning = limitations.speed_warning
        self.torque_warning = limitations.torque_warning
        self.power_warning = limitations.power_warning


@dataclass
class ConfigDateTime:
    #  是否开启自动从GPS同步UTC时间
    sync_with_gps = False
    utc: datetime = None
    system: datetime = None
    date_format: str = None

    def set_default_value(self):
        dateTimeConf: DateTimeConf = DateTimeConf.get()
        self.sync_with_gps = dateTimeConf.sync_with_gps
        self.utc = dateTimeConf.utc_date_time
        self.system = dateTimeConf.system_date_time
        self.date_format = dateTimeConf.date_format


@dataclass
class ConfigTest:
    auto_testing = False
    test_mode_running: bool = False
    start_time = None

    def set_default_value(self):
        pass


@dataclass
class ConfigGps:
    raw_data = None
    location = None

    def set_default_value(self):
        self.raw_data = ""


@dataclass
class ConfigOffline:
    # 默认离线数值
    torque: int = 0
    thrust: int = 0
    speed: float = 0.0

    def set_default_value(self):
        offline_default_value: OfflineDefaultValue = OfflineDefaultValue.get()
        self.thrust = offline_default_value.thrust_default_value
        self.torque = offline_default_value.torque_default_value
        self.speed = offline_default_value.speed_default_value


@dataclass
class ConfigSPS:
    speed: float = 0.0
    torque: int = 0
    thrust: int = 0
    power: int = 0

    ad0 = 0
    ad1 = 0

    torque_offset = 0
    thrust_offset = 0

    power_history: list[tuple[float, datetime]] = field(default_factory=list)

    # 0x03 配置相关参数
    ch_sel_1 = None
    gain_1 = None
    ch_sel_0 = None
    gain_0 = None
    speed_sel = None
    sample_rate = None

    # 根据配置时间，从sps累积的平均值
    accumulated_data_ad0_ad1_speed: list[tuple[float, float, float]] = field(default_factory=list)
    # 每秒累积
    accumulated_data_ad0_ad1_speed_for_1s: list[tuple[float, float, float]] = field(default_factory=list)
    # 每秒累计计算的功率
    power_for_1s = 0
    # 15s累积
    accumulated_data_ad0_ad1_speed_for_15s: list[tuple[float, float, float]] = field(default_factory=list)
    speed_for_15s: float = 0.0
    torque_for_15s: int = 0
    power_for_15s: int = 0

    zero_cal_torque_running = False
    zero_cal_thrust_running = False
    zero_cal_ad0_for_torque: list[float] = field(default_factory=list)
    zero_cal_ad1_for_thrust: list[float] = field(default_factory=list)

    def set_default_value(self):
        # get the last accepted zero cal. record.
        sps_accepted_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(ZeroCalInfo.name == 'sps').order_by(ZeroCalInfo.id.desc()).first()
        if sps_accepted_zero_cal is not None:
            self.torque_offset = sps_accepted_zero_cal.torque_offset
            self.thrust_offset = sps_accepted_zero_cal.thrust_offset


@dataclass
class ConfigSPS2:
    speed: float = 0.0
    power: int = 0
    torque: int = 0
    thrust: int = 0

    ad0 = 0
    ad1 = 0

    torque_offset = 0
    thrust_offset = 0

    power_history: list[tuple[float, datetime]] = field(default_factory=list)

    # 0x03 配置相关参数
    ch_sel_1 = None
    gain_1 = None
    ch_sel_0 = None
    gain_0 = None
    speed_sel = None
    sample_rate = None

    # 根据配置时间，从sps累积的平均值
    accumulated_data_ad0_ad1_speed: list[tuple[float, float, float]] = field(default_factory=list)
    # 每秒累积
    accumulated_data_ad0_ad1_speed_for_1s: list[tuple[float, float, float]] = field(default_factory=list)
    # 每秒累计计算的功率
    power_for_1s = 0
    # 15s累积，报告用
    accumulated_data_ad0_ad1_speed_for_15s: list[tuple[float, float, float]] = field(default_factory=list)
    speed_for_15s: float = 0.0
    torque_for_15s: int = 0
    power_for_15s: int = 0

    zero_cal_torque_running = False
    zero_cal_thrust_running = False
    zero_cal_ad0_for_torque: list[float] = field(default_factory=list)
    zero_cal_ad1_for_thrust: list[float] = field(default_factory=list)

    def set_default_value(self):
        sps2_accepted_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(ZeroCalInfo.name == 'sps2').order_by(ZeroCalInfo.id.desc()).first()
        if sps2_accepted_zero_cal is not None:
            self.sps2_torque_offset = sps2_accepted_zero_cal.torque_offset
            self.sps2_thrust_offset = sps2_accepted_zero_cal.thrust_offset


@dataclass
class ConfigCounterSPS:
    @dataclass
    class Interval:
        start_at: datetime | None = None
        times: int = 0
        sum_power: int = 0
        sum_speed: float = 0.0

        avg_power: int = 0
        total_energy: int = 0
        avg_speed: float = 0.0

    @dataclass
    class Total:
        start_at: datetime | None = None
        times: int = 0
        sum_power: int = 0
        sum_speed: float = 0.0

        avg_power: int = 0
        total_energy: int = 0
        avg_speed: float = 0.0

    @dataclass
    class Manually:
        status: Literal["stopped", "reset", "running"] | None = "stopped"
        start_at: datetime | None = None
        stop_at: datetime | None = None
        times: int = 0
        sum_power: int = 0
        sum_speed: float = 0.0

        avg_power: int = 0
        total_energy: int = 0
        avg_speed: float = 0.0

    def set_default_value(self):
        counter_log: CounterLog = CounterLog.get_or_none(CounterLog.sps_name == 'sps')
        if not counter_log:
            CounterLog.create(sps_name='sps', start_utc_date_time=gdata.configDateTime.utc)
        else:
            ConfigCounterSPS.Total.start_at = counter_log.start_utc_date_time
            ConfigCounterSPS.Total.times = counter_log.times
            ConfigCounterSPS.Total.sum_power = counter_log.sum_power
            ConfigCounterSPS.Total.sum_speed = counter_log.sum_speed


@dataclass
class ConfigCounterSPS2:
    @dataclass
    class Interval:
        start_at: datetime | None = None
        times: int = 0
        sum_power: int = 0
        sum_speed: float = 0.0

        avg_power: int = 0
        total_energy: int = 0
        avg_speed: float = 0.0

    class Total:
        start_at: datetime | None = None
        times: int = 0
        sum_power: int = 0
        sum_speed: float = 0.0

        avg_power: int = 0
        total_energy: int = 0
        avg_speed: float = 0.0

    @dataclass
    class Manually:
        status: Literal["stopped", "reset", "running"] | None = "stopped"
        start_at: datetime | None = None
        stop_at: datetime | None = None
        times: int = 0
        sum_power: int = 0
        sum_speed: float = 0.0

        avg_power: int = 0
        total_energy: int = 0
        avg_speed: float = 0.0

    def set_default_value(self):
        counter_log: CounterLog = CounterLog.get_or_none(CounterLog.sps_name == 'sps2')
        if not counter_log:
            if gdata.configCommon.is_twins:
                CounterLog.create(sps_name='sps2', start_utc_date_time=gdata.configDateTime.utc)
        else:
            ConfigCounterSPS.Total.start_at = counter_log.start_utc_date_time
            ConfigCounterSPS.Total.times = counter_log.times
            ConfigCounterSPS.Total.sum_power = counter_log.sum_power
            ConfigCounterSPS.Total.sum_speed = counter_log.sum_speed


@dataclass
class ConfigEvent:
    not_confirmed_count: int = 0

    def set_default_value(self):
        self.not_confirmed_count = EventLog.select(fn.COUNT(EventLog.id)).where(EventLog.breach_reason.is_null()).scalar()


@dataclass
class ConfigIO:
    plc_enabled = None
    plc_ip = None
    plc_port = None
    gps_ip = None
    gps_port = None
    hmi_server_ip = None
    hmi_server_port = None
    sps_ip = None
    sps_port = None
    sps2_ip = None
    sps2_port = None
    output_torque = None
    output_thrust = None
    output_power = None
    output_speed = None
    output_avg_power = None
    output_total_energy = None
    output_com_port = None

    def set_default_value(self):
        io_conf: IOConf = IOConf.get()
        self.plc_enabled = io_conf.plc_enabled
        self.plc_ip = io_conf.plc_ip
        self.plc_port = io_conf.plc_port
        self.gps_ip = io_conf.gps_ip
        self.gps_port = io_conf.gps_port
        self.hmi_server_ip = io_conf.hmi_server_ip
        self.hmi_server_port = io_conf.hmi_server_port
        self.sps_ip = io_conf.sps_ip
        self.sps_port = io_conf.sps_port
        self.sps2_ip = io_conf.sps2_ip
        self.sps2_port = io_conf.sps2_port
        self.output_torque = io_conf.output_torque
        self.output_thrust = io_conf.output_thrust
        self.output_power = io_conf.output_power
        self.output_speed = io_conf.output_speed
        self.output_avg_power = io_conf.output_avg_power
        self.output_total_energy = io_conf.output_total_energy
        self.output_com_port = io_conf.output_com_port


@dataclass
class ConfigFactor:
    # 计算参数
    bearing_outer_diameter_D = 0
    bearing_inner_diameter_d = 0
    elastic_modulus_E = 0
    poisson_ratio_mu = 0
    sensitivity_factor_k = 0

    def set_default_value(self):
        factor_conf: FactorConf = FactorConf.get()
        self.bearing_outer_diameter_D = factor_conf.bearing_outer_diameter_D
        self.bearing_inner_diameter_d = factor_conf.bearing_inner_diameter_d
        self.elastic_modulus_E = factor_conf.elastic_modulus_E
        self.poisson_ratio_mu = factor_conf.poisson_ratio_mu
        self.sensitivity_factor_k = factor_conf.sensitivity_factor_k


@dataclass
class ConfigPropperCurve:
    speed_of_mcr = 0
    power_of_mcr = 0
    speed_of_torque_load_limit = 0
    power_of_torque_load_limit = 0
    power_of_overload = 0
    enable_power_overload_alarm = False

    def set_default_value(self):
        propellerSetting: PropellerSetting = PropellerSetting.get()
        self.speed_of_mcr = propellerSetting.rpm_of_mcr_operating_point
        self.power_of_mcr = propellerSetting.shaft_power_of_mcr_operating_point
        self.speed_of_torque_load_limit = propellerSetting.rpm_right_of_torque_load_limit_curve
        self.power_of_torque_load_limit = propellerSetting.bhp_right_of_torque_load_limit_curve + propellerSetting.value_of_overload_curve
        self.power_of_overload = propellerSetting.value_of_overload_curve
        self.enable_power_overload_alarm = propellerSetting.enable_power_overload_alarm


@dataclass
class GlobalData:
    configCommon = None
    configPreference = None
    configDateTime = None
    configLimitation = None
    configTest = None
    configGps = None
    configOffline = None
    configSPS = None
    configSPS2 = None
    configIO = None
    configFactor = None
    configPropperCurve = None
    configCounterSPS = None
    configCounterSPS2 = None
    configAlarm = None

    def set_default_value(self):
        self.configCommon = ConfigCommon()
        self.configCommon.set_default_value()

        self.configPreference = ConfigPreference()
        self.configPreference.set_default_value()

        self.configDateTime = ConfigDateTime()
        self.configDateTime.set_default_value()

        self.configLimitation = ConfigLimitation()
        self.configLimitation.set_default_value()

        self.configTest = ConfigTest()
        self.configTest.set_default_value()

        self.configGps = ConfigGps()
        self.configGps.set_default_value()

        self.configOffline = ConfigOffline()
        self.configOffline.set_default_value()

        self.configSPS = ConfigSPS()
        self.configSPS.set_default_value()

        self.configSPS2 = ConfigSPS2()
        self.configSPS2.set_default_value()

        self.configFactor = ConfigFactor()
        self.configFactor.set_default_value()

        self.configIO = ConfigIO()
        self.configIO.set_default_value()

        self.configPropperCurve = ConfigPropperCurve()
        self.configPropperCurve.set_default_value()

        self.configCounterSPS = ConfigCounterSPS()
        self.configCounterSPS.set_default_value()

        self.configCounterSPS2 = ConfigCounterSPS2()
        self.configCounterSPS2.set_default_value()

        self.configAlarm = ConfigAlarm()
        self.configAlarm.set_default_value()

        self.configEvent = ConfigEvent()
        self.configEvent.set_default_value()


gdata: GlobalData = GlobalData()
