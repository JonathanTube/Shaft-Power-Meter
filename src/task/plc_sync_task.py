import asyncio
import logging
from typing import Optional
from pymodbus.client import AsyncModbusTcpClient
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.io_conf import IOConf
from common.global_data import gdata


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
            while gdata.is_master and self._retry < self._max_retries:
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
                    self.save_plc_alarm()
                finally:
                    #  指数退避
                    await asyncio.sleep(2 ** self._retry)
                    self._retry += 1

            self._is_canceled = False

    async def heart_beat(self):
        while gdata.is_master and self.plc_client is not None and self.plc_client.connected:
            if self._is_canceled:
                return

            try:
                self._is_connected = True
                self._retry = 0
                await self.handle_alarms()
            except:
                logging.error('exception occured at PlcSyncTask.heart_beat')
                self.save_plc_alarm()
            finally:
                await asyncio.sleep(5)

        # 到达这里，说明连接丢失
        self._is_connected = False
        self.save_plc_alarm()

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
            scaled_values = (
                int(power / 100),  # 功率 kw
                int(torque / 100),  # 扭矩 kNm
                int(thrust / 100),  # 推力 kN
                int(speed * 10)  # 速度 rpm * 10
            )

            # logging.info(f"[***PLC***] write real time data to plc: {scaled_values}")

            await self.plc_client.write_register(12301, scaled_values[0])
            await self.plc_client.write_register(12311, scaled_values[1])
            await self.plc_client.write_register(12321, scaled_values[2])
            await self.plc_client.write_register(12331, scaled_values[3])
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
            self.save_plc_alarm()

    def save_plc_alarm(self):
        try:
            cnt: int = AlarmLog.select().where(AlarmLog.alarm_type == AlarmType.MASTER_PLC_DISCONNECTED, AlarmLog.is_recovery == False).count()
            if cnt == 0:
                logging.info('[***PLC***] create alarm')
                AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=AlarmType.MASTER_PLC_DISCONNECTED, is_from_master=gdata.is_master)
            else:
                logging.info('[***PLC***] alarm exists, skip')
        except:
            logging.error('save PLC alarm failed.')

    async def handle_alarms(self):
        try:
            logging.info('[***PLC***] recovery PLC Alarm')
            AlarmLog.update(is_recovery=True).where(AlarmLog.alarm_type == AlarmType.MASTER_PLC_DISCONNECTED).execute()

            cnt: int = AlarmLog.select().where(AlarmLog.is_recovery == False).count()
            if cnt == 0:
                logging.info(f'[***PLC***], check none of alarm, clear all plc alarm.')
                await plc.write_alarm(False)
            else:
                await plc.write_alarm(True)
        except:
            logging.error('recovery PLC alarm failed.')


# 全局单例
plc: PlcSyncTask = PlcSyncTask()
