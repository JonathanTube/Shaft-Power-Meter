import logging
import struct
from common.global_data import gdata
from jm3846.JM3846_util import JM3846Util


class JM38460x03:
    @staticmethod
    def build_request() -> bytes:
        return struct.pack(
            ">HHHBBHH",
            0x0003,   # 事务标识符
            0x0000,   # 协议标识符固定0x0000
            6,        # 长度字段 = 1 + 1 + 2 + 2 = 6
            0xFF,     # Unit ID固定0xFF
            0x03,     # 功能码：0x03
            0x0000,   # 起始地址：0x0000（大端序，寄存器 40001）
            0x0006    # 寄存器数量
        )

    @staticmethod
    def parse_response(data: bytes, name: str):
        try:
            # 解析MBAP头
            _, _, length, _ = struct.unpack(">HHHB", data[:7])
            # 解析PDU部分
            pdu = data[7:7 + length - 1]

            byte_count = pdu[1]
            data_bytes = pdu[2:2 + byte_count]

            # 解析寄存器值
            values = [struct.unpack(">H", data_bytes[i:i+2])[0]
                      for i in range(0, byte_count, 2)]

            if name == 'sps':
                gdata.configSPS.ch_sel_1 = (values[2] >> 8) & 0xFF
                gdata.configSPS.gain_1 = JM38460x03.parse_gain((values[3] >> 8) & 0xFF)
                gdata.configSPS.ch_sel_0 = values[2] & 0xFF
                gdata.configSPS.gain_0 = JM38460x03.parse_gain(values[3] & 0xFF)
                gdata.configSPS.speed_sel = bool(values[4] & 0x01)
                gdata.configSPS.sample_rate = values[5]
            else:
                gdata.configSPS2.ch_sel_1 = (values[2] >> 8) & 0xFF
                gdata.configSPS2.gain_1 = JM38460x03.parse_gain((values[3] >> 8) & 0xFF)
                gdata.configSPS2.ch_sel_0 = values[2] & 0xFF
                gdata.configSPS2.gain_0 = JM38460x03.parse_gain(values[3] & 0xFF)
                gdata.configSPS2.speed_sel = bool(values[4] & 0x01)
                gdata.configSPS2.sample_rate = values[5]
        except:
            logging.exception(f"exception occured at JM38460x03Async.parse_response")

    @staticmethod
    def parse_gain(reg_value: int) -> int:
        d = {
            6: 64,
            7: 128
        }
        return d.get(reg_value, 128)  # 默认返回128

    async def handle(name, reader, writer):
        """功能码0x03：读取配置参数"""
        request = JM38460x03.build_request()
        logging.info(f'[JM3846-{name}] send 0x03 req hex={bytes.hex(request)}')
        writer.write(request)
        await writer.drain()

        response = await JM3846Util.read_frame(reader)
        logging.info(f'[JM3846-{name}] send 0x03 res hex={bytes.hex(response)}')

        func_code = struct.unpack(">B", response[7:8])[0]
        if func_code == 0x03:
            JM38460x03.parse_response(response, name)
