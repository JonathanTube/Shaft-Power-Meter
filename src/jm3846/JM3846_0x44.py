import logging
from math import ceil
import struct
from typing import Dict, Optional


class JM38460x44Async:
    @staticmethod
    def build_request(tid: int, frame_size: int, total_frames: int) -> bytes:
        """
        构建0x44功能码请求帧
        返回: bytes类型请求数据
        """
        return struct.pack(
            '>HHHBBHHH',
            tid,
            0x0000,         # 协议标识符固定0x0000
            8,              # 长度字段 = 1 + 1 + 2 + 2 + 2= 8
            0xFF,           # Unit ID固定0xFF
            0x44,           # 自定义功能码
            0x0000,         # 必须为0（文档6.4.2）
            frame_size,     # 每帧寄存器数
            total_frames    # 总帧数
        )

    @staticmethod
    def parse_response(data: bytes, frame_size: int, sample_rate: int, ch_sel1: int, ch_sel0: int, speed_sel: int) -> Optional[Dict]:
        # print('data=', data)
        """
        解析0x44功能码响应
        参数:
            data: 原始字节数据
            ch_sel1: 通道1选择参数
            ch_sel0: 通道0选择参数
            speed_sel: 速度选择参数
        返回: 解析后的字典或None
        """
        # 基本头长度检查
        if len(data) < 12:
            return {'success': False, 'error': '数据长度不足'}

        try:
            # 解析MBAP头
            transaction_id, protocol_id, length, unit_id = struct.unpack(">HHHB", data[:7])
            func_code = data[7]

            # 异常响应处理
            if func_code & 0x80:
                error_code = data[8] if len(data) >= 9 else 0
                return {
                    'success': False,
                    'error_code': error_code,
                    'transaction_id': transaction_id
                }

            # 功能码校验
            if func_code != 0x44:
                return {
                    'success': False,
                    'error': f'无效功能码: 0x{func_code:02x}',
                    'transaction_id': transaction_id
                }

            # 解析帧信息
            current_frame = struct.unpack('>H', data[8:10])[0]
            total_frames = struct.unpack('>H', data[10:12])[0]

            # print('len(data)=', len(data))  # 212
            # print('length=', length)  # 206
            # 计算有效载荷长度
            payload_length = length - 5  # 从长度字段减去unit_id(1)和func_code(1) # 206 - 5 = 201
            payload_start = 12
            payload_end = payload_start + payload_length  # 12 + 201 = 213

            payload = data[payload_start: payload_end]

            # 解析小端序数据
            values = []
            for i in range(0, len(payload), 2):
                if i+1 >= len(payload):
                    break
                # 小端序，无符号整型
                values.append(struct.unpack('<H', payload[i:i+2])[0])

            channel_count: int = JM38460x44Async.get_channel_count(ch_sel1, ch_sel0, speed_sel)
            frames_per_second: int = JM38460x44Async.get_frames_per_second(channel_count, sample_rate, frame_size)
            first_frame_per_second = current_frame % frames_per_second == 0
            print('first_frame_per_second=', first_frame_per_second)
            result = {
                'success': True,
                'func_code': func_code,
                'transaction_id': transaction_id,
                'protocol_id': protocol_id,
                'unit_id': unit_id,
                'current_frame': current_frame + 1,
                'total_frames': total_frames,
                'first_frame_per_second': first_frame_per_second,  # 是否1s数据范围内的第一帧
                'values': JM38460x44Async.convert_data(values, ch_sel1, ch_sel0, speed_sel)
            }

            # print(result)

            return result
        except struct.error as e:
            logging.exception(f"JM38460x44Async.parse_response")
            return {'success': False, 'error': f'解包错误: {str(e)}'}
        except Exception as e:
            logging.exception(f"JM38460x44Async.parse_response")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_channel_count(ch_sel1: int, ch_sel0: int, speed_sel: int):
        if ch_sel1 != 0 and ch_sel0 != 0 and speed_sel == 1:
            return 3
        return 2

    @staticmethod
    def get_frames_per_second(channel_count: int, sample_rate: int, frame_size: int):
        # 2字节 * 通道数 * 采样率hz / 帧大小 = 传输1s的数据需要多少帧
        frames_per_second = (2 * channel_count * sample_rate) / frame_size
        return ceil(frames_per_second)

    @staticmethod
    def convert_data(values: list[int], ch_sel1: int, ch_sel0: int, speed_sel: int):
        # print(values)
        # CH_SEL1\CH_SEL0 都不为0且SPEED_SEL=1时：ch0-ch1-rpm-ch0-ch1-rpm-；
        # CH_SEL1\CH_SEL0 都不为4\0且SPEED_SEL=1时： ch1-rpm -ch1-rpm-;
        # CH_SEL1\CH_SEL0 都不为0\1且SPEED_SEL=1时： ch0-rpm -ch0-rpm-;
        # CH_SEL1\CH_SEL0 都不为1\1且SPEED_SEL=0时： ch0-ch1 -ch0-ch1-；
        ch0_sum = 0
        ch1_sum = 0
        rpm_sum = 0
        values_length = len(values)
        if ch_sel1 != 0 and ch_sel0 != 0 and speed_sel == 1:
            channel_count = 3
            part_length = values_length / channel_count
            for i in range(0, values_length, channel_count):
                chunk = values[i: i + channel_count]
                # print(f'i = {i}, chunk[0]={chunk[0]}')
                ch0_sum += chunk[0]
                ch1_sum += chunk[1]
                rpm_sum += chunk[2]
            ch0_ad = ch0_sum / part_length
            ch1_ad = ch1_sum / part_length
            rpm = rpm_sum / part_length
            return {
                'ch0_ad': ch0_ad,
                'ch1_ad': ch1_ad,
                'rpm': rpm
            }

        if ch_sel1 != 4 and ch_sel0 != 0 and speed_sel == 1:
            channel_count = 2
            part_length = values_length / channel_count
            for i in range(0, values_length, channel_count):
                chunk = values[i: i + channel_count]
                ch1_sum += chunk[0]
                rpm_sum += chunk[1]
            ch1_ad = ch1_sum / part_length
            rpm = rpm_sum / part_length
            return {
                'ch1_ad': ch1_ad,
                'rpm': rpm
            }

        if ch_sel1 != 0 and ch_sel0 != 1 and speed_sel == 1:
            channel_count = 2
            part_length = values_length / channel_count
            for i in range(0, values_length, channel_count):
                chunk = values[i: i + channel_count]
                ch0_sum += chunk[0]
                rpm_sum += chunk[1]
            ch0_ad = ch0_sum / part_length
            rpm = rpm_sum / part_length
            return {
                'ch0_ad': ch0_ad,
                'rpm': rpm
            }

        if ch_sel1 != 1 and ch_sel0 != 1 and speed_sel == 0:
            channel_count = 2
            part_length = values_length / channel_count
            for i in range(0, values_length, channel_count):
                chunk = values[i: i + channel_count]
                ch0_sum += chunk[0]
                ch1_sum += chunk[1]
            ch0_ad = ch0_sum / part_length
            ch1_ad = ch1_sum / part_length
            return {
                'ch0_ad': ch0_ad,
                'ch1_ad': ch1_ad
            }

        return {
            'ch0_ad': 0,
            'ch1_ad': 0,
            'rpm': 0
        }
