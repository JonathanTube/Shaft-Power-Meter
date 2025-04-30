import asyncio
import logging
from typing import Optional
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException
from common.const_alarm_type import AlarmType
from common.global_data import gdata
from db.models.alarm_log import AlarmLog
from db.models.io_conf import IOConf


class PLCUtil:
    def __init__(self):
        self._lock = asyncio.Lock()  # 线程安全锁
        self.plc_client: Optional[AsyncModbusTcpClient] = None
        self._is_connecting = False  # 防止重复重连
        self._max_retries = 3  # 最大重连次数

    async def auto_reconnect(self) -> bool:
        async with self._lock:  # 确保单线程重连
            if self.plc_client and self.plc_client.connected:
                return True

            for attempt in range(self._max_retries):
                try:
                    if self._is_connecting:
                        return False

                    self._is_connecting = True
                    # 初始化或重新创建客户端
                    if not self.plc_client:
                        io_conf = IOConf.get()
                        self.plc_client = AsyncModbusTcpClient(
                            host=io_conf.plc_ip,
                            port=io_conf.plc_port,
                            timeout=10,
                            retries=3,
                            reconnect_delay=5  # 自动重连间隔
                        )

                    await self.plc_client.connect()
                    if self.plc_client.connected:
                        logging.info("PLC connected successfully")
                        self._is_connecting = False
                        return True

                except Exception as e:
                    logging.warning(f"PLC {attempt + 1}th reconnect failed: {str(e)}")
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                finally:
                    self._is_connecting = False

            # 重连失败创建报警
            self.save_alarm()
            return False

    async def read_4_20_ma_data(self) -> dict:
        if not await self.auto_reconnect():
            return self._empty_4_20ma_data()

        try:
            return {  # 全部使用async/await
                "power_range_min": await self._safe_read(12298),
                "power_range_max": await self._safe_read(12299),
                "power_range_offset": await self._safe_read(12300),

                "torque_range_min": await self._safe_read(12308),
                "torque_range_max": await self._safe_read(12309),
                "torque_range_offset": await self._safe_read(12310),

                "thrust_range_min": await self._safe_read(12318),
                "thrust_range_max": await self._safe_read(12319),
                "thrust_range_offset": await self._safe_read(12320),

                "speed_range_min": await self._safe_read(12328),
                "speed_range_max": await self._safe_read(12329),
                "speed_range_offset": await self._safe_read(12330)
            }
        except ConnectionException as e:
            logging.error(f"PLC connection error: {e}")
            self.save_alarm()
        except Exception as e:
            logging.error(f"PLC read data unknown error: {e}")
            self.save_alarm()
        return self._empty_4_20ma_data()

    async def write_4_20_ma_data(self, data: dict) -> bool:
        if not await self.auto_reconnect():
            return False

        try:
            await self.plc_client.write_register(12298, int(data["power_range_min"]))
            await self.plc_client.write_register(12299, int(data["power_range_max"]))
            await self.plc_client.write_register(12300, int(data["power_range_offset"]))

            await self.plc_client.write_register(12308, int(data["torque_range_min"]))
            await self.plc_client.write_register(12309, int(data["torque_range_max"]))
            await self.plc_client.write_register(12310, int(data["torque_range_offset"]))

            await self.plc_client.write_register(12318, int(data["thrust_range_min"]))
            await self.plc_client.write_register(12319, int(data["thrust_range_max"]))
            await self.plc_client.write_register(12320, int(data["thrust_range_offset"]))

            await self.plc_client.write_register(12328, int(data["speed_range_min"]))
            await self.plc_client.write_register(12329, int(data["speed_range_max"]))
            await self.plc_client.write_register(12330, int(data["speed_range_offset"]))
            return True
        except Exception as e:
            logging.error(f"PLC write data failed: {e}")
            self.save_alarm()

        return False

    async def write_instant_data(self, power: float, torque: float, thrust: float, speed: float) -> bool:
        if not await self.auto_reconnect():
            return False

        scaled_values = (
            int(power / 1000),
            int(torque / 1000),
            int(thrust / 1000),
            int(speed)
        )

        try:
            await self.plc_client.write_register(12301, scaled_values[0])
            await self.plc_client.write_register(12311, scaled_values[1])
            await self.plc_client.write_register(12321, scaled_values[2])
            await self.plc_client.write_register(12331, scaled_values[3])
            return True
        except Exception as e:
            logging.error(f"PLC write data failed: {e}")
            self.save_alarm()
            return False

    async def write_alarm(self, occured: bool) -> bool:
        if not await self.auto_reconnect():
            return False

        try:
            await self.plc_client.write_register(12288, 1 if occured else 0)
            logging.info(f"PLC write alarm: {occured}")
            return True
        except Exception as e:
            logging.error(f"PLC write alarm failed: {e}")
            self.save_alarm()
        return False

    async def write_overload(self, occured: bool) -> bool:
        if not await self.auto_reconnect():
            return False

        try:
            await self.plc_client.write_register(12289, 1 if occured else 0)
            logging.info(f"PLC write eexi breach: {occured}")
            return True
        except Exception as e:
            logging.error(f"PLC write eexi breach failed: {e}")
            self.save_alarm()
        return False

    async def read_alarm(self) -> bool:
        if not await self.auto_reconnect():
            return False

        try:
            return await self._safe_read(12288) == 1
        except Exception as e:
            logging.error(f"PLC read alarm failed: {e}")
            self.save_alarm()
            return False

    async def read_eexi_overload(self) -> bool:
        if not await self.auto_reconnect():
            return False
        try:
            return await self._safe_read(12289) == 1
        except Exception as e:
            logging.error(f"PLC read eexi breach failed: {e}")
            self.save_alarm()
            return False

    async def _safe_read(self, address: int) -> Optional[int]:
        try:
            if not self.plc_client.connected:
                return None
            response = await self.plc_client.read_holding_registers(address)
            return response.registers[0] if not response.isError() else None
        except Exception as e:
            logging.warning(f"PLC address {address} read failed: {e}")
            self.save_alarm()
            return None

    def _empty_4_20ma_data(self) -> dict:
        return {key: None for key in [
            "power_range_min", "power_range_max", "power_range_offset",
            "torque_range_min", "torque_range_max", "torque_range_offset",
            "thrust_range_min", "thrust_range_max", "thrust_range_offset",
            "speed_range_min", "speed_range_max", "speed_range_offset"
        ]}

    async def close(self):
        if self.plc_client and self.plc_client.connected:
            await self.plc_client.close()

    def save_alarm(self):
        AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=AlarmType.PLC_DISCONNECTED)


# 全局单例
plc_util: PLCUtil = PLCUtil()
