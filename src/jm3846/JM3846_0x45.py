import struct
import logging
from typing import Dict, Optional


class JM38460x45Async:
    """异步版本的功能码0x45处理器"""

    @staticmethod
    def build_request(tid: int) -> bytes:
        """
        构建0x45功能码请求帧
        返回: bytes类型请求数据
        """
        return struct.pack(
            '>HHHBB',
            tid,
            0x0000,         # 协议标识符固定0x0000
            2,              # 长度字段 = 1 + 1 = 2
            0xFF,           # Unit ID固定0xFF
            0x45            # 自定义功能码
        )

    @staticmethod
    def parse_response(data: bytes) -> Optional[Dict]:
        """
        解析0x45功能码响应
        参数: data - 原始字节数据
        返回: 解析后的字典或None
        """

        try:
            # 解析MBAP头
            transaction_id, protocol_id, length, unit_id = struct.unpack(">HHHB", data[:7])
            func_code = data[7]

            # 验证响应长度
            expected_length = 2  # 根据协议文档定义
            if length != expected_length:
                return {
                    'success': False,
                    'error': f'长度字段不匹配: 预期{expected_length} 实际{length}',
                    'transaction_id': transaction_id
                }

            return {
                'success': True,
                'func_code': func_code,
                'transaction_id': transaction_id,
                'protocol_id': protocol_id,
                'unit_id': unit_id
            }
        except struct.error as e:
            logging.exception(f"JM38460x45Async.parse_response")
            return {
                'success': False,
                'error': f'解包错误: {str(e)}',
                'transaction_id': transaction_id if 'transaction_id' in locals() else None
            }
        except Exception as e:
            logging.exception(f"JM38460x45Async.parse_response")
            return {
                'success': False,
                'error': str(e),
                'transaction_id': transaction_id if 'transaction_id' in locals() else None
            }
