import asyncio
import logging
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator
from jm3846.JM3846_thrust_util import JM3846ThrustUtil


class JM3846Thrust:

    def __init__(self) -> None:
        # 默认是10s内数据
        self.accumulated_data: list[int] = []

        self.is_running = False
        self.name = None

    async def start(self, name):
        self.name = name
        self.is_running = True
        while self.is_running:
            # 清理数据
            self.accumulated_data.clear()
            # 等待数据累积
            await asyncio.sleep(10)

            if gdata.test_mode_running:
                break

            # 处理数据
            if gdata.zero_cal_sps_thrust_is_running:
                logging.info('test mode is running, skip recording thrust.')
                continue

            ch1_ad = JM3846ThrustUtil.get_avg(self.accumulated_data)
            self.handle_result(ch1_ad)

    def stop(self):
        self.is_running = False

    def handle_result(self, ch1_ad):
        try:
            if ch1_ad is None:
                return

            ad1_mv_per_v = JM3846Calculator.calculate_mv_per_v(ch1_ad, gdata.gain_1)
            # 加上偏移量
            thrust_offset = gdata.sps_thrust_offset if self.name == 'sps' else gdata.sps2_thrust_offset
            ad1_mv_per_v += thrust_offset
            thrust = JM3846Calculator.calculate_thrust(ad1_mv_per_v)
            logging.info(f'name=[***{self.name}***],ad1={ch1_ad},ad1_mv_per_v={ad1_mv_per_v}, thrust_offset={thrust_offset}, thrust={thrust}')

            if self.name == 'sps':
                gdata.sps_ad1 = ch1_ad
                gdata.sps_thrust = thrust
            elif self.name == 'sps2':
                gdata.sps2_ad1 = ch1_ad
                gdata.sps2_thrust = thrust

        except:
            logging.exception('exception occured at JM3846Thrust.handle_result')


jm3846_thrust: JM3846Thrust = JM3846Thrust()
