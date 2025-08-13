import asyncio
import logging
from typing import Optional
from pymodbus.client import AsyncModbusTcpClient
from common.const_alarm_type import AlarmType
from db.models.io_conf import IOConf
from utils.alarm_saver import AlarmSaver


# 寄存器映射表（高位在前、低位在后）
REGISTER_MAP = {
    # 功率配置区（4-20mA 对应范围）
    "power_range_min": (12349, 12348),   # %MW11 (高), %MW10 (低)
    "power_range_max": (12353, 12352),   # %MW13 (高), %MW12 (低)
    "power_range_offset": (12357, 12356),  # %MW15 (高), %MW14 (低)

    # 实时功率（模拟量）
    "instant_power": (12361, 12360)      # %MW17 (高), %MW16 (低)
}


class PlcSyncTask:
    def __init__(self):
        self._lock = asyncio.Lock()  # 连接锁，防止并发连接
        self.plc_client: Optional[AsyncModbusTcpClient] = None
        self.is_online = False

    async def connect(self):
        """连接PLC（非阻塞）"""
        async with self._lock:
            try:
                io_conf: IOConf = IOConf.get()
                ip = io_conf.plc_ip
                port = io_conf.plc_port

                logging.info(f'[PLC] 正在连接 {ip}:{port}')
                self.plc_client = AsyncModbusTcpClient(
                    host=ip,
                    port=port,
                    timeout=5,          # 每次请求超时
                    retries=5,          # 每次请求重试次数
                    reconnect_delay=5   # 重试间隔
                )
                await self.plc_client.connect()
            except Exception as e:
                logging.error(f'[PLC] 连接失败: {e}')
                self.set_offline()

    async def read_4_20_ma_data(self) -> dict:
        """读取 4-20mA 配置数据"""
        if not self.is_connected():
            return self._empty_4_20ma_data()

        try:
            return {
                # 功率范围 32 位
                "power_range_min": await self.read_register_32(*REGISTER_MAP["power_range_min"]),
                "power_range_max": await self.read_register_32(*REGISTER_MAP["power_range_max"]),
                "power_range_offset": await self.read_register_32(*REGISTER_MAP["power_range_offset"]),

                # 其他保持原逻辑
                "torque_range_min": await self.read_register(12308),
                "torque_range_max": await self.read_register(12309),
                "torque_range_offset": await self.read_register(12310),
                "thrust_range_min": await self.read_register(12318),
                "thrust_range_max": await self.read_register(12319),
                "thrust_range_offset": await self.read_register(12320),
                "speed_range_min": await self.read_register(12328),
                "speed_range_max": await self.read_register(12329),
                "speed_range_offset": await self.read_register(12330)
            }
        except Exception as e:
            logging.error(f'[PLC] 读取 4-20mA 数据失败: {e}')
            return self._empty_4_20ma_data()

    async def write_4_20_ma_data(self, data: dict):
        """写入 4-20mA 配置数据"""
        if not self.is_connected():
            return

        logging.info(f"[PLC] 写入 4-20mA 数据: {data}")

        try:
            # 功率相关（32 位）
            await self.write_register_32(*REGISTER_MAP["power_range_min"], int(data["power_range_min"]))
            await self.write_register_32(*REGISTER_MAP["power_range_max"], int(data["power_range_max"]))
            await self.write_register_32(*REGISTER_MAP["power_range_offset"], int(data["power_range_offset"]))

            # 其他保持原逻辑
            await self.plc_client.write_register(12308, int(data["torque_range_min"]))
            await self.plc_client.write_register(12309, int(data["torque_range_max"]))
            await self.plc_client.write_register(12310, int(data["torque_range_offset"]))
            await self.plc_client.write_register(12318, int(data["thrust_range_min"]))
            await self.plc_client.write_register(12319, int(data["thrust_range_max"]))
            await self.plc_client.write_register(12320, int(data["thrust_range_offset"]))
            await self.plc_client.write_register(12328, int(data["speed_range_min"]))
            await self.plc_client.write_register(12329, int(data["speed_range_max"]))
            await self.plc_client.write_register(12330, int(data["speed_range_offset"]))
        except Exception as e:
            logging.error(f"[PLC] 写入 4-20mA 数据失败: {e}")

    async def read_instant_data(self) -> dict:
        if not self.is_connected():
            return {"power": None, "torque": None, "thrust": None, "speed": None}

        try:
            return {
                "power": await self.read_register_32(*REGISTER_MAP["instant_power"]),
                "torque": await self.read_register(12311),
                "thrust": await self.read_register(12321),
                "speed": await self.read_register(12331)
            }
        except:
            logging.error(f"[PLC] 读取实时数据失败")

        return {"power": None, "torque": None, "thrust": None, "speed": None}

    async def write_instant_data(self, power: float, torque: float, thrust: float, speed: float):
        """
        写入实时数据到PLC
        - 功率为 32 位，高位在前低位在后
        - 其他保持原逻辑
        """
        if not self.is_connected():
            return False

        try:
            _power = int(power / 100)
            _torque = int(torque / 100)
            _thrust = int(thrust / 100)
            _speed = int(speed * 10)

            logging.info(f"[PLC] 写入实时数据power={_power},torque={_torque},_thrust={_thrust},_speed={_speed}")
            # 写入功率（32 位）
            await self.write_register_32(*REGISTER_MAP["instant_power"], _power)

            # 其他保持原逻辑
            await self.plc_client.write_register(12311, _torque)
            await self.plc_client.write_register(12321, _thrust)
            await self.plc_client.write_register(12331, _speed)
            self.set_online()
        except Exception as e:
            logging.error(f"[PLC] 写入实时数据失败: {e}")
            self.set_offline()

    async def read_alarm(self) -> bool:
        if not self.is_connected():
            return None

        try:
            return await self.read_coil(12288)
        except:
            logging.error(f"[PLC] 读取报警状态失败")
        return None

    async def write_alarm(self, occured: bool):
        """写入报警状态"""
        if not self.is_connected():
            return
        try:
            await self.plc_client.write_coil(address=12288, value=occured)
        except Exception as e:
            logging.error(f"[PLC] 写入报警状态失败: {e}")

    async def read_power_overload(self) -> bool:
        if not self.is_connected:
            return None

        try:
            return await self.read_coil(12289)
        except:
            logging.error(f"[PLC] 读取功率超载报警失败")

    async def write_power_overload(self, occured: bool):
        """写入功率超载报警"""
        if not self.is_connected():
            return
        try:
            await self.plc_client.write_coil(address=12289, value=occured)
        except Exception as e:
            logging.error(f"[PLC] 写入功率超载报警失败: {e}")

    async def read_eexi_breach_alarm(self) -> bool:
        if not self.is_connected:
            return None

        try:
            return await self.read_coil(12290)
        except:
            logging.error(f"[PLC] 读取 EEXI 超限报警失败")

    async def write_eexi_breach_alarm(self, occured: bool):
        """写入 EEXI 超限报警"""
        if not self.is_connected():
            return
        try:
            await self.plc_client.write_coil(address=12290, value=occured)
        except Exception as e:
            logging.error(f"[PLC] 写入 EEXI 超限报警失败: {e}")

    async def read_register(self, address: int) -> Optional[int]:
        resp = await asyncio.wait_for(self.plc_client.read_holding_registers(address), timeout=2)
        return resp.registers[0] if not resp.isError() else None

    async def read_register_32(self, high_addr: int, low_addr: int) -> Optional[int]:
        """读取 32 位（高位在前）"""
        high = await self.read_register(high_addr)
        low = await self.read_register(low_addr)
        if high is None or low is None:
            return None
        return (high << 16) | low

    async def write_register_32(self, high_addr: int, low_addr: int, value: int):
        """写入 32 位（高位在前）"""
        high = (value >> 16) & 0xFFFF
        low = value & 0xFFFF
        await self.plc_client.write_register(high_addr, high)
        await self.plc_client.write_register(low_addr, low)

    async def read_coil(self, address: int) -> Optional[bool]:
        resp = await self.plc_client.read_coils(address, count=1)
        if resp is None or getattr(resp, "isError", lambda: False)():
            return None
        bits = getattr(resp, "bits", None)
        if bits and len(bits) > 0:
            return bool(bits[0])
        return None

    def is_connected(self) -> bool:
        """检查客户端是否可用"""
        return self.plc_client is not None and self.plc_client.connected

    def _empty_4_20ma_data(self) -> dict:
        """返回空的 4-20mA 数据"""
        return {key: 0 for key in [
            "power_range_min", "power_range_max", "power_range_offset",
            "torque_range_min", "torque_range_max", "torque_range_offset",
            "thrust_range_min", "thrust_range_max", "thrust_range_offset",
            "speed_range_min", "speed_range_max", "speed_range_offset"
        ]}

    async def close(self):
        """关闭PLC连接"""
        if not self.is_connected():
            return
        try:
            logging.info('[PLC] 正在关闭PLC连接')
            await self.plc_client.close()
        except Exception as e:
            logging.error(f'[PLC] 关闭PLC连接失败: {e}')
        finally:
            self.set_offline()

    def set_online(self):
        if self.is_online == False:
            self.is_online = True
            AlarmSaver.recovery(AlarmType.MASTER_PLC)

    def set_offline(self):
        if self.is_online:
            self.is_online = False
            AlarmSaver.create(AlarmType.MASTER_PLC)


# 全局单例
plc: PlcSyncTask = PlcSyncTask()
