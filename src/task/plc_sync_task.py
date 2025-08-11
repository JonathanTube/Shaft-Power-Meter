import asyncio
import logging
from peewee import fn
from typing import Optional
from pymodbus.client import AsyncModbusTcpClient
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.io_conf import IOConf
from common.global_data import gdata
from utils.alarm_saver import AlarmSaver


class PlcSyncTask:
    def __init__(self):
        self._lock = asyncio.Lock()  # 线程安全锁
        self.plc_client: Optional[AsyncModbusTcpClient] = None

        self._retry = 0
        self._max_retries = 6  # 最大重连次数
        self._is_connected = False
        self._is_canceled = False

        self.ip = None
        self.port = None

    @property
    def is_connected(self):
        return self._is_connected

    async def connect(self):
        async with self._lock:  # 确保单线程重连

            if self._is_connected:
                return

            self._is_canceled = False

            self._retry = 0
            while gdata.configCommon.is_master and self._retry < self._max_retries:
                # 如果是手动取消，直接跳出
                if self._is_canceled:
                    break

                try:
                    # 重新创建客户端
                    io_conf: IOConf = IOConf.get()
                    self.ip = io_conf.plc_ip
                    self.port = io_conf.plc_port

                    logging.info(f'[***PLC***] connect to plc {self.ip} {self.port}')

                    self.plc_client = AsyncModbusTcpClient(
                        host=io_conf.plc_ip,
                        port=io_conf.plc_port,
                        timeout=5,
                        retries=5,
                        reconnect_delay=5
                    )

                    await self.plc_client.connect()

                    logging.info("[***PLC***] connected successfully")

                    await self.heart_beat()
                except:
                    logging.error(f"[***PLC***] {self._retry + 1}th reconnect failed")
                    AlarmSaver.create(AlarmType.MASTER_PLC)
                finally:
                    #  指数退避
                    await asyncio.sleep(2 ** self._retry)
                    self._retry += 1

            self._is_canceled = False

    async def heart_beat(self):
        while gdata.configCommon.is_master and self.plc_client is not None and self.plc_client.connected:
            if self._is_canceled:
                return

            try:
                self._is_connected = True
                self._retry = 0
                await self.handle_alarm_recovery()
            except:
                logging.error('exception occured at PlcSyncTask.heart_beat')
                AlarmSaver.create(AlarmType.MASTER_PLC)
            finally:
                await asyncio.sleep(5)

        # 到达这里，说明连接丢失
        self._is_connected = False
        AlarmSaver.create(AlarmType.MASTER_PLC)

    async def read_4_20_ma_data(self) -> dict:
        if not self._is_connected:
            return self._empty_4_20ma_data()

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
        except:
            logging.error(f"[***PLC***] {self.ip}:{self.port} PLC connection error")

        return self._empty_4_20ma_data()

    async def write_4_20_ma_data(self, data: dict):

        logging.info(f"PlcSyncTask.write_4_20_ma_data={data}")

        if not self._is_connected:
            return

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
        except:
            raise f"[***PLC***] {self.ip}:{self.port} PLC write data failed"

    async def write_instant_data(self, power: float, torque: float, thrust: float, speed: float):
        try:
            # power的单位是kw，保留一位小数，plc无法显示小数，所以除以1000 再乘以 10，也就是除以100
            _power = int(power / 100)  # 功率 kw
            _torque = int(torque / 100)  # 扭矩 kNm
            _thrust = int(thrust / 100)  # 推力 kN
            _speed = int(speed * 10)  # 速度 rpm * 10

            logging.info(f"[***PLC***] write real time data to plc: power={_power} torque={_torque} thrust={_thrust} speed={_speed}")

            await self.plc_client.write_register(12301, _power)
            await self.plc_client.write_register(12311, _torque)
            await self.plc_client.write_register(12321, _thrust)
            await self.plc_client.write_register(12331, _speed)
        except:
            logging.error(f"[***PLC***] {self.ip}:{self.port} write data failed")

    async def read_instant_data(self) -> dict:
        if not self._is_connected:
            return {"power": None, "torque": None, "thrust": None, "speed": None}

        try:
            return {
                "power": await self._safe_read_register(12301),
                "torque": await self._safe_read_register(12311),
                "thrust": await self._safe_read_register(12321),
                "speed": await self._safe_read_register(12331)
            }
        except:
            logging.error(f"[***PLC***] {self.ip}:{self.port} PLC read data failed")

        return {"power": None, "torque": None, "thrust": None, "speed": None}

    async def write_alarm(self, occured: bool):
        if not self._is_connected:
            return

        try:
            await self.plc_client.write_coil(address=12288, value=occured)
            logging.info(f"[***PLC**] PLC write alarm: {occured}")
        except:
            logging.error(f"[***PLC**] {self.ip}:{self.port} write alarm failed")

    async def write_power_overload(self, occured: bool):
        if not self._is_connected:
            return

        try:
            await self.plc_client.write_coil(address=12289, value=occured)
            logging.info(f"[***PLC***] write power overload: {occured}")
        except:
            logging.error(f"[***PLC***] {self.ip}:{self.port} write power overload failed")

    async def write_eexi_breach_alarm(self, occured):
        logging.info(f'[***PLC***] write_eexi_breach_alarm={occured}')
        if not self._is_connected:
            return

        try:
            await self.plc_client.write_coil(address=12290, value=occured)
            logging.info(f"[***PLC***] write eexi breach: {occured}")
        except:
            logging.error(f"[***PLC***] {self.ip}:{self.port} write eexi breach failed")

    async def read_alarm(self) -> bool:
        if not self._is_connected:
            return

        try:
            return await self._safe_read_coil(12288)
        except:
            logging.error(f"[***PLC***] {self.ip}:{self.port} read alarm failed")

    async def read_power_overload(self) -> bool:
        if not self._is_connected:
            return

        try:
            return await self._safe_read_coil(12289)
        except:
            logging.error(f"[***PLC***] {self.ip}:{self.port} read power overload failed")

    async def _safe_read_register(self, address: int) -> Optional[int]:
        response = await self.plc_client.read_holding_registers(address)
        return response.registers[0] if not response.isError() else None

    async def _safe_read_coil(self, address: int) -> Optional[int]:
        response = await self.plc_client.read_coils(address=address, count=1)
        return response.bits[0] if not response.isError() else None

    def _empty_4_20ma_data(self) -> dict:
        return {key: 0 for key in [
            "power_range_min", "power_range_max", "power_range_offset",
            "torque_range_min", "torque_range_max", "torque_range_offset",
            "thrust_range_min", "thrust_range_max", "thrust_range_offset",
            "speed_range_min", "speed_range_max", "speed_range_offset"
        ]}

    async def close(self):
        self._is_canceled = True

        if not self._is_connected:
            return

        try:
            logging.info('[***PLC***] close plc connection')
            if self.plc_client and self.plc_client.connected:
                await self.plc_client.close()
        except:
            logging.error("[***PLC***] close plc error occured")
        finally:
            self._is_connected = False

    async def handle_alarm_recovery(self):
        try:
            logging.info('[***PLC***] recovery PLC Alarm')
            # 恢复PLC
            AlarmSaver.recovery(AlarmType.MASTER_PLC)
            # 是否存在报警
            if self.has_alarms():
                await plc.write_alarm(True)
            else:
                await plc.write_alarm(False)
        except:
            logging.error('recovery PLC alarm failed.')

    def has_alarms(self) -> bool:
        cnt = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(AlarmLog.recovery_time.is_null(True)).scalar()
        return cnt > 0


# 全局单例
plc: PlcSyncTask = PlcSyncTask()
