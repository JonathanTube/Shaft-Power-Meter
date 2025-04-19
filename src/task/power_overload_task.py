import asyncio
from common.global_data import gdata
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from utils.formula_cal import FormulaCalculator
from db.models.alarm_log import AlarmLog
from common.const_alarm_type import AlarmType
import flet as ft
from common.const_pubsub_topic import PubSubTopic

class PowerOverloadTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.breach_times = 0
        self.recovery_times = 0
        self.checking_continuous_interval = 60

    async def start(self):
        system_settings: SystemSettings = SystemSettings.get()
        propeller_setting: PropellerSetting = PropellerSetting.get()
        gdata.enable_power_overload_alarm = propeller_setting.alarm_enabled_of_overload_curve

        # 功率必须突破持续超过60s后，才算突破
        self.checking_continuous_interval = system_settings.eexi_breach_checking_duration
        max_power = propeller_setting.shaft_power_of_mcr_operating_point
        max_speed = propeller_setting.rpm_of_mcr_operating_point
        torque_speed_limit_percent = propeller_setting.bhp_right_of_torque_load_limit_curve

        while True:
            # 如果功率过载曲线报警未开启，则不进行功率过载报警
            if gdata.enable_power_overload_alarm == False:
                self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_POWER_OVERLOAD_OCCURED, False)
                await asyncio.sleep(5)
                continue

            # 获取当前转速
            sps1_speed = gdata.sps1_speed
            sps2_speed = gdata.sps2_speed
            # 获取当前功率
            sps1_instant_power = gdata.sps1_power
            # print(f'sps1_instant_power={sps1_instant_power}')
            sps2_instant_power = gdata.sps2_power
            # print(f'sps2_instant_power={sps2_instant_power}')

            sps1_expected_power = FormulaCalculator.calculate_power_by_speed(
                max_power, max_speed, torque_speed_limit_percent, sps1_speed)
            # print(f'sps1_expected_power={sps1_expected_power}')
            sps2_expected_power = FormulaCalculator.calculate_power_by_speed(
                max_power, max_speed, torque_speed_limit_percent, sps2_speed)
            # print(f'sps2_expected_power={sps2_expected_power}')

            if sps1_instant_power > sps1_expected_power or sps2_instant_power > sps2_expected_power:
                self.__handle_breach_event()
            else:
                self.__handle_recovery_event()
            await asyncio.sleep(1)

    def __handle_breach_event(self):
        self.breach_times += 1
        # 连续突破60s，则记录突破事件
        # print(f'self.breach_times={self.checking_continuous_interval}')
        if self.breach_times == self.checking_continuous_interval:
            self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_POWER_OVERLOAD_OCCURED, True)
            AlarmLog.create(
                utc_date_time=gdata.utc_date_time,
                alarm_type=AlarmType.POWER_OVERLOAD
            )

    def __handle_recovery_event(self):
        if self.breach_times < self.checking_continuous_interval:
            self.__reset_all()
            return

        self.recovery_times += 1
        if self.recovery_times == self.checking_continuous_interval:
            self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_POWER_OVERLOAD_OCCURED, False)

    def __reset_all(self):
        self.breach_times = 0
        self.recovery_times = 0
