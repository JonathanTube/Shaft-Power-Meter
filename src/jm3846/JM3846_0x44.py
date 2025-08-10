import asyncio
import logging
import struct
from common.global_data import gdata
from jm3846.JM3846_0x45 import JM38460x45
from jm3846.JM3846_torque_rpm import jm3846_torque_rpm
from jm3846.JM3846_thrust import jm3846_thrust
from jm3846.JM3846_util import JM3846Util


class JM38460x44:
    frame_size = 120
    total_frames = 0xFFFF
    running = False

    @staticmethod
    def build_request(frame_size: int, total_frames: int) -> bytes:
        """
        构建0x44功能码请求帧
        返回: bytes类型请求数据
        """
        return struct.pack(
            '>HHHBBHHH',
            0x0044,         # 事务标识符
            0x0000,         # 协议标识符固定0x0000
            8,              # 长度字段 = 1 + 1 + 2 + 2 + 2= 8
            0xFF,           # Unit ID固定0xFF
            0x44,           # 自定义功能码
            0x0000,         # 必须为0（文档6.4.2）
            frame_size,     # 每帧寄存器数
            total_frames    # 总帧数
        )

    @staticmethod
    def parse_response(data: bytes, name: str) -> int:
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

            if name == 'sps':
                if gdata.configSPS.zero_cal_torque_running:
                    gdata.configSPS.zero_cal_ad0_for_torque.append(data)
                else:
                    jm3846_torque_rpm.accumulated_data.append(data)

                if gdata.configSPS.zero_cal_thrust_running:
                    gdata.configSPS.zero_cal_ad1_for_thrust.append(data)
                else:
                    jm3846_thrust.accumulated_data.append(data)
            else:
                if gdata.configSPS2.zero_cal_torque_running:
                    gdata.configSPS2.zero_cal_ad0_for_torque.append(data)
                else:
                    jm3846_torque_rpm.accumulated_data.append(data)

                if gdata.configSPS2.zero_cal_thrust_running:
                    gdata.configSPS2.zero_cal_ad1_for_thrust.append(data)
                else:
                    jm3846_thrust.accumulated_data.append(data)

        return current_frame

    @staticmethod
    async def handle(name, reader, writer):
        """功能码0x44：请求多帧数据"""
        request = JM38460x44.build_request(JM38460x44.frame_size, JM38460x44.total_frames)
        logging.info(f'[JM3846-{name}] send 0x44 req hex={bytes.hex(request)}')
        writer.write(request)
        await writer.drain()

        JM38460x44.running = True
        _receive_0x44_task = asyncio.create_task(JM38460x44.receive_0x44(name, reader))
        await _receive_0x44_task

    @staticmethod
    async def receive_0x44(name, reader):
        """持续接收数据"""
        while JM38460x44.running:
            response = await JM3846Util.read_frame(reader)
            func_code = struct.unpack(">B", response[7:8])[0]

            # 异常码
            if func_code & 0x80:
                continue

            if func_code == 0x44:
                current_frame = JM38460x44.parse_response(response, name)

                if current_frame >= JM38460x44.total_frames:
                    JM38460x44.running = False
                    break

        # 断开事务
        await JM38460x45.handle()
        # 重新开始
        await JM38460x44.handle()
