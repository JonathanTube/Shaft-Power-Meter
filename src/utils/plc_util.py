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
        self._max_retries = 999999999  # 最大重连次数

        self.ip = None
        self.port = None

    async def auto_reconnect(self, only_once:bool = False) -> bool:
        async with self._lock:  # 确保单线程重连
            if self.plc_client and self.plc_client.connected:
                gdata.connected_to_plc = True
                return True

            try_times = 1 if only_once else self._max_retries
            for attempt in range(try_times):
                if not gdata.plc_enabled:
                    gdata.connected_to_plc = False
                    return False
                try:
                    if self._is_connecting:
                        return False

                    self._is_connecting = True
                    self.close()
                    # 重新创建客户端
                    io_conf:IOConf = IOConf.get()
                    self.ip = io_conf.plc_ip
                    self.port = io_conf.plc_port

                    logging.info(f'connect to plc {self.ip} {self.port}')

                    self.plc_client = AsyncModbusTcpClient(
                        host=io_conf.plc_ip,
                        port=io_conf.plc_port,
                        timeout=5,
                        retries=3,
                        reconnect_delay=5  # 自动重连间隔
                    )

                    await self.plc_client.connect()
                    if self.plc_client.connected:
                        logging.info("PLC connected successfully")
                        self._is_connecting = False
                        gdata.connected_to_plc  = True
                        return True

                except Exception:
                    logging.exception(f"PLC {attempt + 1}th reconnect failed")
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                    gdata.connected_to_plc = False
                finally:
                    self._is_connecting = False

            # 重连失败创建报警
            self.save_alarm()
            return False

    async def read_4_20_ma_data(self) -> dict:
        try:
            return {  # 全部使用async/await
                "power_range_min": await self._safe_read_register(12298),
                "power_range_max": await self._safe_read_register(12299),
                "power_range_offset": await self._safe_read_register(12300),

                "torque_range_min": await self._safe_read_register(12308),
                "torque_range_max": await self._safe_read_register(12309),
                "torque_range_offset": await self._safe_read_register(12310),

                "thrust_range_min": await self._safe_read_register(12318),
                "thrust_range_max": await self._safe_read_register(12319),
                "thrust_range_offset": await self._safe_read_register(12320),

                "speed_range_min": await self._safe_read_register(12328),
                "speed_range_max": await self._safe_read_register(12329),
                "speed_range_offset": await self._safe_read_register(12330)
            }
        except ConnectionException:
            logging.error(f"{self.ip}:{self.port} PLC connection error")
            self.save_alarm()
            gdata.connected_to_plc = False
            await self.auto_reconnect()
        except Exception:
            logging.exception(f"{self.ip}:{self.port} PLC read data unknown error")
            self.save_alarm()
        return self._empty_4_20ma_data()

    async def write_4_20_ma_data(self, data: dict) -> bool:
        if not gdata.plc_enabled or not gdata.connected_to_plc:
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
        except ConnectionException:
            logging.error(f"{self.ip}:{self.port} PLC connection error")
            self.save_alarm()
            gdata.connected_to_plc = False
            await self.auto_reconnect()
        except Exception:
            logging.exception("PLC write data failed")

        return False

    async def write_instant_data(self, power: float, torque: float, thrust: float, speed: float) -> bool:
        if not gdata.plc_enabled or not gdata.connected_to_plc:
            return False

        # power的单位是kw，保留一位小数，plc无法显示小数，所以除以1000 再乘以 10，也就是除以100
        scaled_values = (
            int(power / 100),  # 功率 kw
            int(torque / 100),  # 扭矩 kNm
            int(thrust / 100),  # 推力 kN
            int(speed * 10)  # 速度 rpm * 10
        )

        logging.info(f"write real time data to plc: {scaled_values}")

        try:
            await self.plc_client.write_register(12301, scaled_values[0])
            await self.plc_client.write_register(12311, scaled_values[1])
            await self.plc_client.write_register(12321, scaled_values[2])
            await self.plc_client.write_register(12331, scaled_values[3])
            return True
        except ConnectionException:
            logging.error(f"{self.ip}:{self.port} PLC connection error")
            self.save_alarm()
            gdata.connected_to_plc = False
            await self.auto_reconnect()
        except Exception:
            logging.exception("PLC write data failed")
            self.save_alarm()
            return False

    async def read_instant_data(self) -> dict:
        try:
            return {
                "power": await self._safe_read_register(12301),
                "torque": await self._safe_read_register(12311),
                "thrust": await self._safe_read_register(12321),
                "speed": await self._safe_read_register(12331)
            }
        except ConnectionException:
            logging.error(f"{self.ip}:{self.port} PLC connection error")
            self.save_alarm()
            gdata.connected_to_plc = False
            await self.auto_reconnect()
        except Exception:
            logging.exception(f"{self.ip}:{self.port} PLC read data failed")
            self.save_alarm()
            return self._empty_instant_data()

    def _empty_instant_data(self) -> dict:
        return {
            "power": None,
            "torque": None,
            "thrust": None,
            "speed": None
        }

    async def write_alarm(self, occured: bool) -> bool:
        if not gdata.plc_enabled or not gdata.connected_to_plc:
            return False

        try:
            await self.plc_client.write_coil(address=12288, value=occured)
            logging.info(f"PLC write alarm: {occured}")
            return True
        except ConnectionException:
            logging.error(f"{self.ip}:{self.port} PLC connection error")
            self.save_alarm()
            gdata.connected_to_plc = False
            await self.auto_reconnect()
        except Exception:
            logging.exception("PLC write alarm failed")
            self.save_alarm()
        return False

    async def write_power_overload(self, occured: bool) -> bool:
        if not gdata.plc_enabled or not gdata.connected_to_plc:
            return False

        try:
            await self.plc_client.write_coil(address=12289, value=occured)
            logging.info(f"PLC write power overload: {occured}")
            return True
        except ConnectionException:
            logging.error(f"{self.ip}:{self.port} PLC connection error")
            self.save_alarm()
            gdata.connected_to_plc = False
            await self.auto_reconnect()
        except Exception:
            logging.exception("PLC write power overload failed")
            self.save_alarm()
        return False

    async def read_alarm(self) -> bool:
        try:
            return await self._safe_read_coil(12288)
        except ConnectionException:
            logging.error(f"{self.ip}:{self.port} PLC connection error")
            self.save_alarm()
            gdata.connected_to_plc = False
            await self.auto_reconnect()
        except Exception:
            logging.exception("PLC read alarm failed")
            self.save_alarm()
            return False

    async def read_power_overload(self) -> bool:
        try:
            return await self._safe_read_coil(12289)
        except ConnectionException:
            logging.error(f"{self.ip}:{self.port} PLC connection error")
            self.save_alarm()
            gdata.connected_to_plc = False
            await self.auto_reconnect()
        except Exception:
            logging.exception("PLC read power overload failed")
            self.save_alarm()
            return False

    async def _safe_read_register(self, address: int) -> Optional[int]:
        try:
            if not self.plc_client.connected:
                return None
            response = await self.plc_client.read_holding_registers(address)
            return response.registers[0] if not response.isError() else None
        except Exception:
            logging.exception(f"PLC address {address} read failed")
            self.save_alarm()
            return None

    async def _safe_read_coil(self, address: int) -> Optional[int]:
        try:
            if not self.plc_client.connected:
                return None
            response = await self.plc_client.read_coils(address=address, count=1)
            return response.bits[0] if not response.isError() else None
        except Exception:
            logging.exception(f"PLC address {address} read failed")
            self.save_alarm()
            return None

    def _empty_4_20ma_data(self) -> dict:
        return {key: None for key in [
            "power_range_min", "power_range_max", "power_range_offset",
            "torque_range_min", "torque_range_max", "torque_range_offset",
            "thrust_range_min", "thrust_range_max", "thrust_range_offset",
            "speed_range_min", "speed_range_max", "speed_range_offset"
        ]}

    def close(self):
        try:
            if self.plc_client and self.plc_client.connected:
                self.plc_client.close()
                gdata.connected_to_plc = False
        except Exception:
            logging.exception("close plc error occured")
            return False
        return True        

    def save_alarm(self):
        cnt: int = AlarmLog.select().where(AlarmLog.alarm_type == AlarmType.PLC_DISCONNECTED, AlarmLog.acknowledge_time.is_null()).count()
        if cnt == 0:
            AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=AlarmType.PLC_DISCONNECTED)


# 全局单例
plc_util: PLCUtil = PLCUtil()
