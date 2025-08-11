import asyncio
import struct
import logging


class JM3846Util:
    @staticmethod
    async def read_frame(reader) -> bytes | None:
        """按 Modbus TCP(MBAP) 帧格式读取一帧，连接断开或超时返回 None"""
        try:
            header = await asyncio.wait_for(reader.readexactly(6), timeout=10)
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
            body = await asyncio.wait_for(reader.readexactly(length), timeout=10)
        except asyncio.IncompleteReadError:
            logging.warning("[JM3846] 连接断开（读取主体失败）")
            return None
        except asyncio.TimeoutError:
            logging.warning("[JM3846] 读取主体超时")
            return None

        return header + body
