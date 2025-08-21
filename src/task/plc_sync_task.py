import asyncio
import logging
from typing import Optional
from pymodbus.client import AsyncModbusTcpClient
from common.const_alarm_type import AlarmType
from utils.alarm_saver import AlarmSaver
from common.global_data import gdata

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
        self.is_online = False       # 仅表示 TCP 连接是否建立
        self.is_canceled = False

    async def connect(self):
        """连接PLC（非阻塞）"""
        if not gdata.configCommon.is_master:
            return

        if not gdata.configIO.plc_enabled:
            return

        async with self._lock:
            try:
                self.is_canceled = False
                ip = gdata.configIO.plc_ip
                port = gdata.configIO.plc_port
                logging.info(f'[PLC] 正在连接 {ip}:{port}')
                self.plc_client = AsyncModbusTcpClient(
                    host=ip,
                    port=port,
                    timeout=10,          # 每次请求超时
                    retries=0          # 每次请求重试次数
                )
                await self.plc_client.connect()
                if self.is_connected():
                    self.set_online()
                    logging.info(f'[PLC] 已连接 {ip}:{port}')
                else:
                    self.set_offline()
                    logging.error('[PLC] 连接失败（底层未建立）')
            except Exception as e:
                logging.exception(f'[PLC] 连接异常: {e}')
                self.set_offline()

    async def read_4_20_ma_data(self) -> dict:
        """读取 4-20mA 配置数据"""
        if not self.is_connected():
            return self._empty_4_20ma_data()
        try:
            return {
                # 功率范围 32 位（原子读取）
                "power_range_min": await self.read_register_32(*REGISTER_MAP["power_range_min"]),
                "power_range_max": await self.read_register_32(*REGISTER_MAP["power_range_max"]),
                "power_range_offset": await self.read_register_32(*REGISTER_MAP["power_range_offset"]),
                # 其他保持原逻辑（16位）
                "torque_range_min": await self.read_register(12308),
                "torque_range_max": await self.read_register(12309),
                "torque_range_offset": await self.read_register(12310),
                "thrust_range_min": await self.read_register(12318),
                "thrust_range_max": await self.read_register(12319),
                "thrust_range_offset": await self.read_register(12320),
                "speed_range_min": await self.read_register(12328),
                "speed_range_max": await self.read_register(12329),
                "speed_range_offset": await self.read_register(12330),
            }
        except Exception as e:
            logging.exception(f'[PLC] 读取 4-20mA 数据失败: {e}')
            return self._empty_4_20ma_data()

    async def write_4_20_ma_data(self, data: dict):
        """写入 4-20mA 配置数据"""
        logging.info(f"[PLC] 写入 4-20mA 数据: {data}")
        if not self.is_connected():
            return
        try:
            # 功率相关（32 位，原子写入）
            await self.write_register_32(*REGISTER_MAP["power_range_min"], int(data["power_range_min"]))
            await self.write_register_32(*REGISTER_MAP["power_range_max"], int(data["power_range_max"]))
            await self.write_register_32(*REGISTER_MAP["power_range_offset"], int(data["power_range_offset"]))
            # 其他保持原逻辑（16位）
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
            logging.exception("[PLC] 写入 4-20mA 数据失败: %s", e)

    async def read_instant_data(self) -> dict:
        if not self.is_connected():
            return {"power": None, "torque": None, "thrust": None, "speed": None}
        try:
            return {
                "power": await self.read_register_32(*REGISTER_MAP["instant_power"]),
                "torque": await self.read_register(12311),
                "thrust": await self.read_register(12321),
                "speed": await self.read_register(12331),
            }
        except Exception as e:
            logging.exception("[PLC] 读取实时数据失败: %s", e)
            return {"power": None, "torque": None, "thrust": None, "speed": None}

    async def write_instant_data(self, power: int, torque: int, thrust: int, speed: float):
        """写入实时数据到PLC，失败自动重连"""
        try:
            if self.is_canceled:
                return

            if not self.is_connected() and not self.is_canceled:
                logging.warning("[PLC] 未连接，尝试重连...")
                await self.release()
                await asyncio.sleep(3)
                await self.connect()
                if not self.is_connected():
                    logging.error("[PLC] 重连失败，写入中止")
                    return False

            _power = round(power / 1000)
            _torque = round(torque / 1000)
            _thrust = round(thrust / 1000)
            _speed = round(speed * 10)

            # 原子写入 32 位功率
            await self.write_register_32(*REGISTER_MAP["instant_power"], _power)

            # 写入 16 位寄存器
            if _torque <= 65535:
                await self.plc_client.write_register(12311, _torque)
            else:
                logging.error(f'torque to plc is too big,{_torque}')

            if _thrust <= 65535:
                await self.plc_client.write_register(12321, _thrust)
            else:
                logging.error(f'thrust to plc is too big,{_thrust}')

            if _speed <= 65535:
                await self.plc_client.write_register(12331, _speed)
            else:
                logging.error(f'speed to plc is too big,{_speed}')

            return True

        except Exception as e:
            logging.error(f"[PLC] 写入实时数据失败: {e}, 尝试重连...")
            # 写入失败 -> 停止连接，清空 client
            await self.release()
            if not self.is_canceled:
                await asyncio.sleep(3)
                # 尝试重连一次
                await self.connect()
                if self.is_connected():
                    logging.info("[PLC] 重连成功，可以重新写入")
                else:
                    logging.error("[PLC] 重连失败")
            return False

    async def read_alarm(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return await self.read_coil(12288)
        except Exception as e:
            logging.exception("[PLC] 读取报警状态失败: %s", e)
            return None

    async def write_common_alarm(self, occured: bool):
        """写入报警状态"""
        logging.info(f'[PLC] 写入公共报警状态={occured}')
        if not self.is_connected():
            return
        try:
            await self.plc_client.write_coil(address=12288, value=occured)
        except Exception as e:
            logging.exception("[PLC] 写入报警状态失败: %s", e)

    async def read_power_overload(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return await self.read_coil(12289)
        except Exception as e:
            logging.exception("[PLC] 读取功率超载报警失败: %s", e)
            return None

    async def write_power_overload(self, occured: bool):
        """写入功率超载报警"""
        logging.info(f'[PLC] 写入功率超载报警={occured}')
        if not self.is_connected():
            return
        try:
            await self.plc_client.write_coil(address=12289, value=occured)
        except Exception as e:
            logging.exception("[PLC] 写入功率超载报警失败: %s", e)

    async def read_eexi_breach_alarm(self) -> Optional[bool]:
        if not self.is_connected():
            return None
        try:
            return await self.read_coil(12290)
        except Exception as e:
            logging.exception("[PLC] 读取 EEXI 超限报警失败: %s", e)
            return None

    async def write_eexi_breach_alarm(self, occured: bool):
        """写入 EEXI 超限报警"""
        logging.info(f'[PLC] 写入 EEXI 超限报警={occured}')
        if not self.is_connected():
            return
        try:
            await self.plc_client.write_coil(address=12290, value=occured)
        except Exception as e:
            logging.exception("[PLC] 写入 EEXI 超限报警失败: %s", e)

    # ---------------- 低层读写封装 ----------------

    async def read_register(self, address: int) -> Optional[int]:
        try:
            resp = await asyncio.wait_for(self.plc_client.read_holding_registers(address, count=1), timeout=2)
            if resp is None or getattr(resp, "isError", lambda: True)():
                return None
            regs = getattr(resp, "registers", None)
            return regs[0] if regs else None
        except:
            return 0

    async def read_register_32(self, high_addr: int, low_addr: int) -> Optional[int]:
        """读取 32 位（高位在前）——一次读两个寄存器，避免不一致"""
        try:
            # 以高地址为起点读两个寄存器： [high, low]
            resp = await asyncio.wait_for(self.plc_client.read_holding_registers(high_addr, count=2), timeout=2)
            if resp is None or getattr(resp, "isError", lambda: True)():
                return None
            regs = getattr(resp, "registers", [])
            if len(regs) < 2:
                return None
            return (int(regs[0]) << 16) | int(regs[1])
        except:
            return 0

    async def write_register_32(self, high_addr: int, low_addr: int, value: int):
        """写入 32 位（高位在前）——一次写两个寄存器，保持原子性"""
        high = (int(value) >> 16) & 0xFFFF
        low = int(value) & 0xFFFF
        # 从高位地址起写两个值：[high, low]
        await self.plc_client.write_registers(high_addr, [high, low])

    async def read_coil(self, address: int) -> Optional[bool]:
        resp = await asyncio.wait_for(self.plc_client.read_coils(address, count=1), timeout=2)
        if resp is None or getattr(resp, "isError", lambda: True)():
            return None
        bits = getattr(resp, "bits", None)
        return bool(bits[0]) if bits else None

    def is_connected(self) -> bool:
        """检查 TCP 是否已连接"""
        return self.plc_client is not None and getattr(self.plc_client, "connected", False)

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
        await self.release()
        self.is_canceled = True

    async def release(self):
        if not self.is_connected():
            return
        try:
            logging.info('[PLC] 正在关闭PLC连接')
            if self.plc_client:
                self.plc_client.close()
        except Exception as e:
            logging.exception('[PLC] 关闭PLC连接失败: %s', e)
        finally:
            self.set_offline()

    # ---------------- 报警状态（仅反映连接本身） ----------------

    def set_online(self):
        self.is_online = True
        AlarmSaver.recovery(AlarmType.MASTER_PLC)

    def set_offline(self):
        self.is_online = False
        AlarmSaver.create(AlarmType.MASTER_PLC)


# 全局单例
plc: PlcSyncTask = PlcSyncTask()
