import asyncio
import logging
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator
from jm3846.JM3846_torque_rpm_util import JM3846TorqueRpmUtil
from utils.unit_parser import UnitParser


class JM3846TorqueRpm:

    def __init__(self) -> None:
        # 2s内数据
        self.accumulated_data: list[int] = []

        self._is_running = False
        self.name = None

    def is_running(self):
        return self._is_running

    async def start(self, name):
        self.name = name
        self._is_running = True
        while self._is_running:
            # 清理数据
            self.accumulated_data.clear()
            # 等待数据累积
            await asyncio.sleep(2)

            if gdata.configTest.test_mode_running:
                continue

            # 处理数据
            result = JM3846TorqueRpmUtil.get_avg(self.accumulated_data, name)
            self.handle_result(result[0], result[1])

    def stop(self):
        self._is_running = False

    def handle_result(self, ch0_ad, rpm):
        try:
            if self.name == 'sps':
                if ch0_ad:
                    gdata.configSPS.ad0 = ch0_ad
                    gdata.configSPS.torque = self.cal_torque(ch0_ad)
                if rpm:
                    gdata.configSPS.speed = rpm
            else:
                if ch0_ad:
                    gdata.configSPS2.ad0 = ch0_ad
                    gdata.configSPS2.torque = self.cal_torque(ch0_ad)
                if rpm:
                    gdata.configSPS2.speed = rpm

        except:
            logging.exception(
                'exception occured at JM3846TorqueRpm.handle_result')

    def cal_torque(self, ch0_ad):
        try:
            torque_offset = gdata.configSPS.torque_offset if self.name == 'sps' else gdata.configSPS2.sps2_torque_offset
            gain_0 = gdata.configSPS.gain_0 if self.name == 'sps' else gdata.configSPS2.gain_0
            ad0_mv_per_v = JM3846Calculator.calculate_mv_per_v(ch0_ad, gain_0)
            # 减去偏移量
            ad0_mv_per_v = ad0_mv_per_v - torque_offset
            ad0_microstrain = JM3846Calculator.calculate_microstrain(ad0_mv_per_v)
            torque = JM3846Calculator.calculate_torque(ad0_microstrain)
            # logging.info(f'{self.name}=>ad0={ch0_ad}, ad0_mv_per_v={ad0_mv_per_v}, torque_offset={torque_offset}, microstrain={ad0_microstrain}, torque={torque}')
            return torque
        except:
            logging.exception(
                'exception occured at JM3846TorqueRpm.cal_torque')

        return 0


jm3846_torque_rpm: JM3846TorqueRpm = JM3846TorqueRpm()
