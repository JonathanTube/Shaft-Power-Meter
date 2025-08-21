import asyncio
from common.global_data import gdata
from jm3846.JM3846_util import JM3846Util
from utils.formula_cal import FormulaCalculator


class JM3846DataHandlerFor1s:
    def __init__(self) -> None:
        self._is_running = False
        self.name = None

    def is_running(self):
        return self._is_running

    async def start(self, name):
        self.name = name
        self._is_running = True
        while self._is_running:
            if gdata.configTest.test_mode_running:
                await asyncio.sleep(1)
                continue

            # 清理数据
            if self.name == 'sps':
                # 处理数据
                ch0_ad, _, rpm = JM3846Util.get_avg(self.name, gdata.configSPS.accumulated_data_ad0_ad1_speed)
                torque = JM3846Util.cal_torque(self.name, ch0_ad)
                # 直接计算power
                gdata.configSPS.power_for_1s = FormulaCalculator.calculate_instant_power(torque, rpm)
                gdata.configSPS.accumulated_data_ad0_ad1_speed.clear()
            else:
                # 处理数据
                ch0_ad, _, rpm = JM3846Util.get_avg(self.name, gdata.configSPS2.accumulated_data_ad0_ad1_speed)
                torque = JM3846Util.cal_torque(self.name, ch0_ad)
                # 直接计算power
                gdata.configSPS2.power_for_1s = FormulaCalculator.calculate_instant_power(torque, rpm)
                gdata.configSPS2.accumulated_data_ad0_ad1_speed.clear()
            # 等待数据累积
            await asyncio.sleep(1)

    def stop(self):
        self._is_running = False


jm3846_data_handler_for_1s: JM3846DataHandlerFor1s = JM3846DataHandlerFor1s()
