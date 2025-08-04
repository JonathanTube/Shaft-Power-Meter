import logging
import struct
from common.global_data import gdata
from jm3846.JM3846_torque_rpm import jm3846_torque_rpm
from jm3846.JM3846_thrust import jm3846_thrust

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
    def parse_response(data: bytes) -> int:
        try:
            # 解析MBAP头
            _, _, length, _ = struct.unpack(">HHHB", data[:7])

            # 解析帧信息
            current_frame = struct.unpack('>H', data[8:10])[0]

            # 计算有效载荷长度
            payload_length = length - 5
            payload_start = 12
            payload_end = payload_start + payload_length  # 12 + 201 = 213

            payload = data[payload_start: payload_end]

            # 解析小端序数据
            for i in range(0, len(payload), 2):
                if i+1 >= len(payload):
                    break
                # 小端序，无符号整型
                data = struct.unpack('<H', payload[i:i+2])[0]

                if gdata.zero_cal_sps_torque_is_running:
                    gdata.zero_cal_sps_ad0_for_torque.append(data)
                else:
                    jm3846_torque_rpm.accumulated_data.append(data)

                if gdata.zero_cal_sps_thrust_is_running:
                    gdata.zero_cal_sps_ad1_for_thrust.append(data)
                else:
                    jm3846_thrust.accumulated_data.append(data)

            return current_frame
        except:
            logging.exception(f"Exception occured at JM38460x44Async.parse_response")

        return 0