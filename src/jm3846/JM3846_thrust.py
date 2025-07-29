import asyncio
import logging
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator


class JM3846Thrust:

    def __init__(self) -> None:
        # 默认是10s内数据
        self.data_accumulate_0x44: list[int] = []

        self.is_running = False
        self.name = None
        self.calc = JM3846Calculator()

    async def start(self, name):
        self.name = name
        self.is_running = True
        while self.is_running:
            # 清理数据
            self.data_accumulate_0x44.clear()
            # 等待数据累积
            await asyncio.sleep(gdata.seconds_of_thrust_collection)
            # 处理数据
            self.convert_data()

    def stop(self):
        self.is_running = False

    def convert_data(self):
        try:
            values_length = len(self.data_accumulate_0x44)
            if values_length == 0:
                return

            ch1_sum = 0

            if gdata.ch_sel_1 != 0 and gdata.ch_sel_0 != 0 and gdata.speed_sel == 1:
                channel_count = 3
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = self.data_accumulate_0x44[i: i + channel_count]
                    ch1_sum += chunk[1]

            elif gdata.ch_sel_1 != 4 and gdata.ch_sel_0 != 0 and gdata.speed_sel == 1:
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = self.data_accumulate_0x44[i: i + channel_count]
                    ch1_sum += chunk[0]

            elif gdata.ch_sel_1 != 1 and gdata.ch_sel_0 != 1 and gdata.speed_sel == 0:
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = self.data_accumulate_0x44[i: i + channel_count]
                    ch1_sum += chunk[1]

            ch1_ad = ch1_sum / part_length

            self.handle_result(ch1_ad)
        except:
            logging.exception('exception occured at JM3846Thrust.convert_data')

    def handle_result(self, ch1_ad):
        try:
            if gdata.test_mode_running:
                return

            if ch1_ad is None:
                return

            ad1 = round(ch1_ad, 2)
            ad1_mv_per_v = self.calc.calculate_mv_per_v(ad1, gdata.gain_1)

            if self.name == 'sps':
                gdata.sps_ad1 = ad1
                gdata.sps_mv_per_v_for_thrust = ad1_mv_per_v
            else:
                gdata.sps2_ad1 = ad1
                gdata.sps2_mv_per_v_for_thrust = ad1_mv_per_v

            # 加上偏移量
            thrust_offset = gdata.sps_thrust_offset if self.name == 'sps' else gdata.sps2_thrust_offset
            ad1_mv_per_v += thrust_offset
            thrust = self.calc.calculate_thrust(ad1_mv_per_v)
            logging.info(f'name=[***{self.name}***],ad1={ad1},ad1_mv_per_v={ad1_mv_per_v}, thrust_offset={thrust_offset}, thrust={thrust}')

            if self.name == 'sps':
                gdata.sps_thrust = thrust
            elif self.name == 'sps2':
                gdata.sps2_thrust = thrust

        except:
            logging.exception('exception occured at JM3846Thrust.handle_result')


jm3846_thrust: JM3846Thrust = JM3846Thrust()
