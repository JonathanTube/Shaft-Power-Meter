import asyncio
import struct
import logging
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator


class JM3846Util:
    @staticmethod
    async def read_frame(reader) -> bytes | None:
        """按 Modbus TCP(MBAP) 帧格式读取一帧，连接断开或超时返回 None"""
        try:
            header = await asyncio.wait_for(reader.readexactly(6), timeout=20)
        except asyncio.IncompleteReadError:
            logging.warning("[JM3846] 连接断开（读取头部失败）")
            return None
        except asyncio.TimeoutError:
            logging.warning("[JM3846] 读取头部超时")
            return None

        length = struct.unpack('>H', header[4:6])[0]
        if length < 2 or length > 2048:
            logging.warning(f"[JM3846] MBAP 长度非法: {length}")
            return None

        try:
            body = await asyncio.wait_for(reader.readexactly(length), timeout=20)
        except asyncio.IncompleteReadError:
            logging.warning("[JM3846] 连接断开（读取主体失败）")
            return None
        except asyncio.TimeoutError:
            logging.warning("[JM3846] 读取主体超时")
            return None

        return header + body

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

    @staticmethod
    def cal_torque(name, ch0_ad):
        try:
            torque_offset = gdata.configSPS.torque_offset if name == 'sps' else gdata.configSPS2.sps2_torque_offset
            gain_0 = gdata.configSPS.gain_0 if name == 'sps' else gdata.configSPS2.gain_0
            ad0_mv_per_v = JM3846Calculator.calculate_mv_per_v(ch0_ad, gain_0)
            # 减去偏移量
            ad0_mv_per_v = ad0_mv_per_v - torque_offset
            ad0_microstrain = JM3846Calculator.calculate_microstrain(ad0_mv_per_v)
            torque = JM3846Calculator.calculate_torque(ad0_microstrain)
            # logging.info(f'{name}=>ad0={ch0_ad}, ad0_mv_per_v={ad0_mv_per_v}, torque_offset={torque_offset}, microstrain={ad0_microstrain}, torque={torque}')
            return torque
        except:
            logging.exception(
                'exception occured at JM3846TorqueRpm.cal_torque')

        return 0

    def cal_thrust(name, ch1_ad):
        try:
            gain_1 = gdata.configSPS.gain_1 if name == 'sps' else gdata.configSPS2.gain_1
            thrust_offset = gdata.configSPS.thrust_offset if name == 'sps' else gdata.configSPS2.thrust_offset

            ad1_mv_per_v = JM3846Calculator.calculate_mv_per_v(ch1_ad, gain_1)
            # 减去偏移量
            ad1_mv_per_v = ad1_mv_per_v - thrust_offset
            thrust = JM3846Calculator.calculate_thrust(ad1_mv_per_v)
            # logging.info(f'{name}=>ad1={ch1_ad},ad1_mv_per_v={ad1_mv_per_v}, thrust_offset={thrust_offset}, thrust={thrust}')
            return thrust
        except:
            logging.exception('exception occured at JM3846Thrust.handle_result')

        return 0
