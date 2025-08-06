import asyncio
import logging
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator
from jm3846.JM3846_thrust_util import JM3846ThrustUtil


class JM3846Thrust:

    def __init__(self) -> None:
        # 默认是10s内数据
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
            await asyncio.sleep(10)

            if gdata.configTest.test_mode_running:
                logging.info('test mode is running, skip recording thrust.')
                break

            if name == 'sps':
                if gdata.configSPS.zero_cal_thrust_running:
                    logging.info('SPS is doing zero cal., skip recording thrust.')
                    continue
            else:
                if gdata.configSPS2.zero_cal_thrust_running:
                    logging.info('SPS2 is doing zero cal., skip recording thrust.')
                    continue

            # 处理数据
            ch1_ad = JM3846ThrustUtil.get_avg(self.accumulated_data, self.name)
            self.handle_result(ch1_ad)

    def stop(self):
        self._is_running = False

    def handle_result(self, ch1_ad):
        try:
            if ch1_ad is None:
                return

            gain_1 = gdata.configSPS.gain_1 if self.name == 'sps' else gdata.configSPS2.gain_1
            thrust_offset = gdata.configSPS.thrust_offset if self.name == 'sps' else gdata.configSPS2.thrust_offset

            ad1_mv_per_v = JM3846Calculator.calculate_mv_per_v(ch1_ad, gain_1)
            # 减去偏移量
            ad1_mv_per_v = ad1_mv_per_v - thrust_offset
            thrust = JM3846Calculator.calculate_thrust(ad1_mv_per_v)
            logging.info(f'name=[***{self.name}***],ad1={ch1_ad},ad1_mv_per_v={ad1_mv_per_v}, thrust_offset={thrust_offset}, thrust={thrust}')

            if self.name == 'sps':
                gdata.configSPS.ad1 = ch1_ad
                gdata.configSPS.thrust = thrust
            elif self.name == 'sps2':
                gdata.configSPS2.ad1 = ch1_ad
                gdata.configSPS2.thrust = thrust

        except:
            logging.exception('exception occured at JM3846Thrust.handle_result')


jm3846_thrust: JM3846Thrust = JM3846Thrust()
