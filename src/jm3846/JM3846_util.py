import asyncio
import struct


class JM3846Util:
    @staticmethod
    async def read_frame(reader) -> bytes:
        """按 Modbus TCP(MBAP) 帧格式读取一帧"""
        header = await asyncio.wait_for(reader.readexactly(6), timeout=10)
        length = struct.unpack('>H', header[4:6])[0]
        if length < 2 or length > 2048:
            raise ValueError(f"Invalid MBAP length: {length}")
        body = await asyncio.wait_for(reader.readexactly(length), timeout=10)
        return header + body
