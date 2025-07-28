import asyncio
import logging
from utils.data_saver import DataSaver
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator


class JM3846DataHandler:

    def __init__(self) -> None:
        self.data_accululation_0x44: list[int] = []
        self.is_running = False
        self.name = None
        self.calc = JM3846Calculator()

    async def start(self, name):
        self.name = name
        self.is_running = True
        while self.is_running:
            self.convert_data()
            await asyncio.sleep(2)

    def stop(self):
        self.is_running = False

    def convert_data(self):
        values_length = len(self.data_accululation_0x44)
        if values_length == 0:
            return
        # CH_SEL1\CH_SEL0 都不为0且SPEED_SEL=1时：ch0-ch1-rpm-ch0-ch1-rpm-；
        # CH_SEL1\CH_SEL0 都不为4\0且SPEED_SEL=1时： ch1-rpm -ch1-rpm-;
        # CH_SEL1\CH_SEL0 都不为0\1且SPEED_SEL=1时： ch0-rpm -ch0-rpm-;
        # CH_SEL1\CH_SEL0 都不为1\1且SPEED_SEL=0时： ch0-ch1 -ch0-ch1-；
        ch0_sum = 0
        ch1_sum = 0
        rpm_sum = 0

        if gdata.ch_sel_1 != 0 and gdata.ch_sel_0 != 0 and gdata.speed_sel == 1:
            channel_count = 3
            part_length = values_length / channel_count
            for i in range(0, values_length, channel_count):
                chunk = self.data_accululation_0x44[i: i + channel_count]
                ch0_sum += chunk[0]
                ch1_sum += chunk[1]
                rpm_sum += chunk[2]

        elif gdata.ch_sel_1 != 4 and gdata.ch_sel_0 != 0 and gdata.speed_sel == 1:
            channel_count = 2
            part_length = values_length / channel_count
            for i in range(0, values_length, channel_count):
                chunk = self.data_accululation_0x44[i: i + channel_count]
                ch1_sum += chunk[0]
                rpm_sum += chunk[1]

        elif gdata.ch_sel_1 != 0 and gdata.ch_sel_0 != 1 and gdata.speed_sel == 1:
            channel_count = 2
            part_length = values_length / channel_count
            for i in range(0, values_length, channel_count):
                chunk = self.data_accululation_0x44[i: i + channel_count]
                ch0_sum += chunk[0]
                rpm_sum += chunk[1]

        elif gdata.ch_sel_1 != 1 and gdata.ch_sel_0 != 1 and gdata.speed_sel == 0:
            channel_count = 2
            part_length = values_length / channel_count
            for i in range(0, values_length, channel_count):
                chunk = self.data_accululation_0x44[i: i + channel_count]
                ch0_sum += chunk[0]
                ch1_sum += chunk[1]

        ch1_ad = ch1_sum / part_length
        ch0_ad = ch0_sum / part_length
        rpm = rpm_sum / part_length

        self.handle_result(ch1_ad, ch0_ad, rpm)

    def handle_result(self, ch1_ad, ch0_ad, rpm):
        try:
            if gdata.test_mode_running:
                logging.info('test mode is running, skip.')
                return

            # 清理数据
            self.data_accululation_0x44.clear()

            torque = 0
            thrust = 0
            speed = 0

            if ch0_ad:
                ad0 = round(ch0_ad, 2)
                ad0_mv_per_v = self.calc.calculate_mv_per_v(ad0, gdata.gain_0)

                if self.name == 'sps':
                    gdata.sps_ad0 = ad0
                    gdata.sps_mv_per_v_for_torque = ad0_mv_per_v
                else:
                    gdata.sps2_ad0 = ad0
                    gdata.sps2_mv_per_v_for_torque = ad0_mv_per_v

                # 加上偏移量
                torque_offset = gdata.sps_torque_offset if self.name == 'sps' else gdata.sps2_torque_offset
                ad0_mv_per_v += torque_offset
                ad0_microstrain = self.calc.calculate_microstrain(ad0_mv_per_v)
                torque = self.calc.calculate_torque(ad0_microstrain)
                logging.info(
                    f'name=[***{self.name}***],ad0={ad0}, ad0_mv_per_v={ad0_mv_per_v}, torque_offset={torque_offset}, microstrain={ad0_microstrain}, torque={torque}'
                )

            if ch1_ad:
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
                logging.info(
                    f'name=[***{self.name}***],ad1={ad1},ad1_mv_per_v={ad1_mv_per_v}, thrust_offset={thrust_offset}, thrust={thrust}'
                )

            if rpm:
                if self.name == 'sps':
                    gdata.sps_speed = round(rpm, 2)
                else:
                    gdata.sps2_speed = round(rpm, 2)

                speed = round(rpm / 10, 1)
                logging.info(
                    f'name=[***{self.name}***], rpm={rpm}, speed={speed}'
                )
            DataSaver.save(self.name, torque, thrust, speed)

        except:
            logging.exception(
                'exception occured at JM3846DataHandler.save_result')


jm3846_data_handler: JM3846DataHandler = JM3846DataHandler()
