import logging
import struct
from typing import Dict


class JM38460x03Async:
    """异步版本的功能码0x03处理器"""

    @staticmethod
    def build_request(tid: int) -> bytes:
        """
        构建0x03功能码请求包
        返回: bytes类型请求数据
        """
        return struct.pack(
            ">HHHBBHH",
            tid,
            0x0000,   # 协议标识符固定0x0000
            6,        # 长度字段 = 1 + 1 + 2 + 2 = 6
            0xFF,     # Unit ID固定0xFF
            0x03,     # 功能码：0x03
            0x0000,   # 起始地址：0x0000（大端序，寄存器 40001）
            0x0006    # 寄存器数量
        )

    @staticmethod
    def parse_response(data: bytes) -> Dict:
        """
        解析0x03功能码响应
        参数: data - 原始字节数据
        返回: 解析后的字典
        """
        try:
            # 解析MBAP头
            transaction_id, protocol_id, length, unit_id = struct.unpack(">HHHB", data[:7])
            func_code = data[7]

            # 解析PDU部分
            pdu = data[7:7 + length - 1]
            if len(pdu) < 2:
                return {'success': False, 'error': 'PDU长度不足'}

            byte_count = pdu[1]
            data_bytes = pdu[2:2 + byte_count]

            if len(data_bytes) != byte_count:
                raise ValueError("数据长度不匹配")

            # 解析寄存器值
            values = [struct.unpack(">H", data_bytes[i:i+2])[0]
                      for i in range(0, byte_count, 2)]

            if len(values) < 6:
                return {'success': False, 'error': '寄存器数量不足'}

            return {
                'success': True,
                'func_code': func_code,
                'transaction_id': transaction_id,
                'protocol_id': protocol_id,
                'unit_id': unit_id,
                'values': {
                    'id': values[0],          # 机号
                    'device_type': values[1],  # 设备类型
                    'ch_sel_0': values[2] & 0xFF,
                    'ch_sel_1': (values[2] >> 8) & 0xFF,
                    'gain_0': JM38460x03Async.parse_gain(values[3] & 0xFF),
                    'gain_1': JM38460x03Async.parse_gain((values[3] >> 8) & 0xFF),
                    'speed_sel': bool(values[4] & 0x01),
                    'sample_rate': values[5]  # 采样率
                }
            }
        except struct.error as e:
            logging.exception(f"JM38460x03Async.parse_response")
            return {'success': False, 'error': f'解包错误: {str(e)}'}
        except Exception as e:
            logging.exception(f"JM38460x03Async.parse_response")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def parse_gain(reg_value: int) -> int:
        """增益值解析（带有效性检查）"""
        if not 0 <= reg_value <= 7:
            raise ValueError(f"无效增益寄存器值: {reg_value}")

        return {
            6: 64,
            7: 128
        }.get(reg_value, 128)  # 默认返回128
