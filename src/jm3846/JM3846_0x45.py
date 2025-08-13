import struct
import logging

from jm3846.JM3846_util import JM3846Util


class JM38460x45:
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
            0x01,           # Unit ID固定0x01
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

    @staticmethod
    async def handle(name: str, reader, writer):
        """功能码0x45：断开数据流"""
        if writer is None or writer.is_closing():
            logging.warning(f"[{name}] connection closed, stopping handle")
            return

        request = JM38460x45.build_request()
        logging.info(f'[JM3846-{name}] send 0x45 req hex={bytes.hex(request)}')

        try:
            writer.write(request)
            await writer.drain()
        except (ConnectionResetError, BrokenPipeError) as e:
            logging.error(f"[{name}] connection error: {e}")
        except Exception:
            logging.exception(f"[{name}] unexpected error in drain")

        frame = await JM3846Util.read_frame(reader)
        if frame is None:
            return  # 优雅退出
        logging.info(f'[JM3846-{name}] send 0x45 res hex={bytes.hex(frame)}')
        func_code = struct.unpack(">B", frame[7:8])[0]
        if func_code == 0x45:
            JM38460x45.parse_response(frame)
