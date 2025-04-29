import asyncio
import logging
from common.global_data import gdata
from db.models.alarm_log import AlarmLog
from common.const_alarm_type import AlarmType


class PowerOverloadTask:
    def __init__(self):
        self.breach_times = 0
        self.recovery_times = 0

    async def start(self):
        while True:
            # 如果功率过载曲线报警未开启，则不进行功率过载报警
            if gdata.enable_power_overload_alarm == False:
                await asyncio.sleep(30)
                continue

            # 获取当前转速
            sps1_speed = gdata.sps1_speed
            sps2_speed = gdata.sps2_speed
            # 获取当前功率
            sps1_power = gdata.sps1_power
            sps2_power = gdata.sps2_power
            # 如果当前的功率超过理论的功率阈值，则记录突破事件,因为是两个SPS，只需要一个超过就算突破
            if self._is_overload(sps1_speed, sps1_power) or self._is_overload(sps2_speed, sps2_power):
                self.__handle_breach_event()
            else:
                self.__handle_recovery_event()
            await asyncio.sleep(gdata.eexi_breach_checking_duration)

    def _is_overload(self, speed, power):
        max_speed = gdata.speed_of_torque_load_limit
        max_power = gdata.power_of_torque_load_limit + gdata.power_of_overload
        # 相对MCR的转速百分比
        speed_percentage = speed / gdata.speed_of_mcr * 100
        # 理论的overload的功率阈值
        overload_power_percentage = round((speed_percentage / max_speed) ** 2 * max_power, 2)
        # 实际的功率百分比
        actual_power_percentage = round(power / gdata.power_of_mcr * 100, 2)
        logging.info(f"power_overload_task: overload_power_percentage={overload_power_percentage}, actual_power_percentage={actual_power_percentage}")
        return actual_power_percentage > overload_power_percentage

    def __handle_breach_event(self):
        self.breach_times += 1
        # 连续突破60s，则记录突破事件
        # 功率必须突破持续超过60s后，才算突破
        if self.breach_times == gdata.eexi_breach_checking_duration:
            AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=AlarmType.POWER_OVERLOAD)

    def __handle_recovery_event(self):
        if self.breach_times < gdata.eexi_breach_checking_duration:
            self.__reset_all()
            return
        self.recovery_times += 1

    def __reset_all(self):
        self.breach_times = 0
        self.recovery_times = 0
