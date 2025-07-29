import asyncio
import logging
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator


class JM3846TorqueRpm:

    def __init__(self) -> None:
        # 2s内数据
        self.data_accumulate_2s_0x44: list[int] = []

        self.is_running = False
        self.name = None
        self.calc = JM3846Calculator()

    async def start(self, name):
        self.name = name
        self.is_running = True
        while self.is_running:
            # 清理数据
            self.data_accumulate_2s_0x44.clear()
            # 等待数据累积
            await asyncio.sleep(2)
            # 处理数据
            self.convert_data()

    def stop(self):
        self.is_running = False

    def convert_data(self):
        try:
            values_length = len(self.data_accumulate_2s_0x44)
            if values_length == 0:
                return
            # CH_SEL1\CH_SEL0 都不为0且SPEED_SEL=1时：ch0-ch1-rpm-ch0-ch1-rpm-；
            # CH_SEL1\CH_SEL0 都不为4\0且SPEED_SEL=1时： ch1-rpm -ch1-rpm-;
            # CH_SEL1\CH_SEL0 都不为0\1且SPEED_SEL=1时： ch0-rpm -ch0-rpm-;
            # CH_SEL1\CH_SEL0 都不为1\1且SPEED_SEL=0时： ch0-ch1 -ch0-ch1-；
            ch0_sum = None
            rpm_sum = None

            if gdata.ch_sel_1 != 0 and gdata.ch_sel_0 != 0 and gdata.speed_sel == 1:
                ch0_sum = 0
                rpm_sum = 0
                channel_count = 3
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = self.data_accumulate_2s_0x44[i: i + channel_count]
                    ch0_sum += chunk[0]
                    rpm_sum += chunk[2]

            elif gdata.ch_sel_1 != 4 and gdata.ch_sel_0 != 0 and gdata.speed_sel == 1:
                rpm_sum = 0
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = self.data_accumulate_2s_0x44[i: i + channel_count]
                    rpm_sum += chunk[1]

            elif gdata.ch_sel_1 != 0 and gdata.ch_sel_0 != 1 and gdata.speed_sel == 1:
                ch0_sum = 0
                rpm_sum = 0
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = self.data_accumulate_2s_0x44[i: i + channel_count]
                    ch0_sum += chunk[0]
                    rpm_sum += chunk[1]

            elif gdata.ch_sel_1 != 1 and gdata.ch_sel_0 != 1 and gdata.speed_sel == 0:
                ch0_sum = 0
                channel_count = 2
                part_length = values_length / channel_count
                for i in range(0, values_length, channel_count):
                    chunk = self.data_accumulate_2s_0x44[i: i + channel_count]
                    ch0_sum += chunk[0]

            ch0_ad = ch0_sum / part_length if ch0_sum else None
            rpm = rpm_sum / part_length if rpm_sum else None

            self.handle_result(ch0_ad, rpm)
        except:
            logging.exception('exception occured at JM3846TorqueRpm.convert_data')

    def handle_result(self, ch0_ad, rpm):
        try:
            if gdata.test_mode_running:
                logging.info('test mode is running, skip.')
                return
                            
            if self.name == 'sps':
                if ch0_ad:
                    gdata.sps_torque = self.cal_torque(ch0_ad)
                if rpm:
                    gdata.sps_speed = round(rpm / 10, 2)
            else:
                if ch0_ad:
                    gdata.sps2_torque = self.cal_torque(ch0_ad)
                if rpm:
                    gdata.sps2_speed = round(rpm / 10, 2)

        except:
            logging.exception('exception occured at JM3846TorqueRpm.handle_result')

    def cal_torque(self, ch0_ad):
        try:
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
            return torque
        except:
            logging.exception('exception occured at JM3846TorqueRpm.cal_torque')

        return 0


jm3846_torque_rpm: JM3846TorqueRpm = JM3846TorqueRpm()
