import asyncio
import logging
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator


class JM3846DataHandler:
    def __init__(self) -> None:
        self._is_running = False
        self.name = None

    def is_running(self):
        return self._is_running

    async def start(self, name):
        self.name = name
        self._is_running = True
        while self._is_running:
            seconds = gdata.configPreference.data_collection_seconds_range
            if gdata.configTest.test_mode_running:
                await asyncio.sleep(seconds)
                continue

            # 清理数据
            if self.name == 'sps':
                gdata.configSPS.accumulated_data_ad0_ad1_speed.clear()
                # 处理数据
                ch0_ad, ch1_ad, rpm = JM3846DataHandler.get_avg(self.name, gdata.configSPS.accumulated_data_ad0_ad1_speed)
                self.handle_result(ch0_ad, ch1_ad, rpm)
            else:
                gdata.configSPS2.accumulated_data_ad0_ad1_speed.clear()
                # 处理数据
                ch0_ad, ch1_ad, rpm = JM3846DataHandler.get_avg(self.name, gdata.configSPS2.accumulated_data_ad0_ad1_speed)
                self.handle_result(ch0_ad, ch1_ad, rpm)

            # 等待数据累积
            await asyncio.sleep(seconds)

    def stop(self):
        self._is_running = False

    def handle_result(self, ch0_ad, ch1_ad, rpm):
        try:
            if self.name == 'sps':
                gdata.configSPS.ad0 = ch0_ad
                gdata.configSPS.ad1 = ch1_ad
                gdata.configSPS.speed = rpm
                gdata.configSPS.torque = self.cal_torque(ch0_ad)
                gdata.configSPS.thrust = self.cal_thrust(ch1_ad)
                # logging.info(f'获取SPS:ad0={round(ch0_ad, 1)},rpm={round(rpm, 1)}')
            else:
                gdata.configSPS2.ad0 = ch0_ad
                gdata.configSPS2.ad1 = ch1_ad
                gdata.configSPS2.speed = rpm
                gdata.configSPS2.torque = self.cal_torque(ch0_ad)
                gdata.configSPS2.thrust = self.cal_thrust(ch1_ad)
                # logging.info(f'获取SPS2:ad0={round(ch0_ad, 1)},rpm={round(rpm, 1)}')
        except:
            logging.exception('exception occured at JM3846TorqueRpm.handle_result')

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

    def cal_thrust(self, ch1_ad):
        try:
            gain_1 = gdata.configSPS.gain_1 if self.name == 'sps' else gdata.configSPS2.gain_1
            thrust_offset = gdata.configSPS.thrust_offset if self.name == 'sps' else gdata.configSPS2.thrust_offset

            ad1_mv_per_v = JM3846Calculator.calculate_mv_per_v(ch1_ad, gain_1)
            # 减去偏移量
            ad1_mv_per_v = ad1_mv_per_v - thrust_offset
            thrust = JM3846Calculator.calculate_thrust(ad1_mv_per_v)
            # logging.info(f'{self.name}=>ad1={ch1_ad},ad1_mv_per_v={ad1_mv_per_v}, thrust_offset={thrust_offset}, thrust={thrust}')
            return thrust
        except:
            logging.exception('exception occured at JM3846Thrust.handle_result')

        return 0

    @staticmethod
    def get_avg(name, accumulated_data) -> tuple[float, float, float]:
        try:
            values_length = len(accumulated_data)
            if values_length == 0:
                return (0, 0, 0)

            # CH_SEL1\CH_SEL0 都不为0且SPEED_SEL=1时：ch0-ch1-rpm-ch0-ch1-rpm-；
            # CH_SEL1\CH_SEL0 都不为4\0且SPEED_SEL=1时： ch1-rpm -ch1-rpm-;
            # CH_SEL1\CH_SEL0 都不为0\1且SPEED_SEL=1时： ch0-rpm -ch0-rpm-;
            # CH_SEL1\CH_SEL0 都不为1\1且SPEED_SEL=0时： ch0-ch1 -ch0-ch1-；
            ch0_sum = 0
            ch1_sum = 0
            rpm_sum = 0
            ch_sel_1 = gdata.configSPS.ch_sel_1 if name == 'sps' else gdata.configSPS2.ch_sel_1
            ch_sel_0 = gdata.configSPS.ch_sel_0 if name == 'sps' else gdata.configSPS2.ch_sel_0
            speed_sel = gdata.configSPS.speed_sel if name == 'sps' else gdata.configSPS2.speed_sel
            channel_count = 3
            # logging.info(f'ch_sel_1={ch_sel_1},ch_sel_0={ch_sel_0},speed_sel={speed_sel}')
            # logging.info(f'data_list={data_list}')
            if ch_sel_1 != 0 and ch_sel_0 != 0 and speed_sel == True:
                ch0_sum = 0
                ch1_sum = 0
                rpm_sum = 0
                channel_count = 3
                for i in range(0, values_length, channel_count):
                    chunk = accumulated_data[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch0_sum += chunk[0]
                        ch1_sum += chunk[1]
                        rpm_sum += chunk[2]

            elif ch_sel_1 != 4 and ch_sel_0 != 0 and speed_sel == True:
                ch1_sum = 0
                rpm_sum = 0
                channel_count = 2
                for i in range(0, values_length, channel_count):
                    chunk = accumulated_data[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch1_sum += chunk[0]
                        rpm_sum += chunk[1]

            elif ch_sel_1 != 0 and ch_sel_0 != 1 and speed_sel == True:
                ch0_sum = 0
                rpm_sum = 0
                channel_count = 2
                for i in range(0, values_length, channel_count):
                    chunk = accumulated_data[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch0_sum += chunk[0]
                        rpm_sum += chunk[1]

            elif ch_sel_1 != 1 and ch_sel_0 != 1 and speed_sel == False:
                ch0_sum = 0
                ch1_sum = 0
                channel_count = 2

                for i in range(0, values_length, channel_count):
                    chunk = accumulated_data[i: i + channel_count]
                    if len(chunk) == channel_count:
                        ch0_sum += chunk[0]
                        ch1_sum += chunk[1]

            part_length = values_length / channel_count
            ch0_ad = round(ch0_sum / part_length, 1)
            ch1_ad = round(ch1_sum / part_length, 1)
            rpm = round(rpm_sum / part_length, 1)

            return (ch0_ad, ch1_ad, rpm)
        except:
            logging.exception('exception occured at JM3846TorqueRpm.convert_data')

        return (0, 0, 0)


jm3846_data_handler: JM3846DataHandler = JM3846DataHandler()
