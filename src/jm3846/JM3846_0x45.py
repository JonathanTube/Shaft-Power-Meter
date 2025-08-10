import struct
import logging


class JM38460x45Async:
    """异步版本的功能码0x45处理器"""

    @staticmethod
    def build_request() -> bytes:
        """
        构建0x45功能码请求帧
        返回: bytes类型请求数据
        """
        return struct.pack(
            '>HHHBB',
            0x0044,         # 事务标识符 和 0x44 保持一致
            0x0000,         # 协议标识符固定0x0000
            2,              # 长度字段 = 1 + 1 = 2
            0xFF,           # Unit ID固定0xFF
            0x45            # 自定义功能码
        )

    @staticmethod
    def parse_response(data: bytes):
        """
        解析0x45功能码响应
        参数: data - 原始字节数据
        返回: 解析后的字典或None
        """
        try:
            func_code = data[7]
            return func_code
        except:
            logging.exception(f"Exception occured at JM38460x45Async.parse_response")
