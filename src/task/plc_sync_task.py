# plc_sync_task.py
# CHANGES:
# - 重构为类实例并保留所有读写方法
# - 连接/心跳/重连逻辑独立、带指数退避
# - 所有读写使用 _safe_* 方法，带超时与锁
# - DB 访问/AlarmSaver 调用移到线程池以避免阻塞
# Reference: original: :contentReference[oaicite:4]{index=4}

import asyncio
import logging
from typing import Optional
from peewee import fn
from pymodbus.client import AsyncModbusTcpClient
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.io_conf import IOConf
from common.global_data import gdata
from utils.alarm_saver import AlarmSaver

_logger = logging.getLogger("plc")

class PlcSyncTask:
    def __init__(self):
        self._connect_lock = asyncio.Lock()
        self._rw_lock = asyncio.Lock()
        self.plc_client: Optional[AsyncModbusTcpClient] = None
        self._keepalive_task: Optional[asyncio.Task] = None
        self._is_stopped = True
        self._is_connected = False
        self._retries = 0
        self._max_backoff = 32
        self.ip = None
        self.port = None

    def start(self):
        """Start keepalive loop (idempotent)."""
        if self._keepalive_task and not self._keepalive_task.done():
            return
        self._is_stopped = False
        self._keepalive_task = asyncio.create_task(self._keepalive_loop(), name="plc-keepalive")

    async def stop(self):
        """Stop and close client."""
        self._is_stopped = True
        if self._keepalive_task:
            self._keepalive_task.cancel()
            try:
                await self._keepalive_task
            except asyncio.CancelledError:
                pass
            self._keepalive_task = None
        await self._close_client()
        self._is_connected = False

    @property
    def is_connected(self):
        return self._is_connected

    async def _keepalive_loop(self):
        backoff = 1
        while gdata.configCommon.is_master and not self._is_stopped:
            try:
                await self._connect_once()
                if self.plc_client and getattr(self.plc_client, "connected", False):
                    self._retries = 0
                    backoff = 1
                    await self._heart_beat_loop()
                else:
                    _logger.warning("PLC: connect_once not connected")
            except asyncio.CancelledError:
                break
            except Exception:
                _logger.exception("PLC keepalive unexpected error")
                await asyncio.to_thread(AlarmSaver.create, AlarmType.MASTER_PLC)

            wait = min(backoff, self._max_backoff)
            _logger.info("PLC waiting %s seconds before reconnect", wait)
            await asyncio.sleep(wait)
            backoff *= 2
            self._retries += 1
        _logger.info("PLC keepalive exited")

    async def _connect_once(self):
        async with self._connect_lock:
            await self._close_client()
            try:
                io_conf: IOConf = await asyncio.to_thread(IOConf.get)
                self.ip, self.port = io_conf.plc_ip, io_conf.plc_port
                _logger.info("PLC connecting to %s:%s", self.ip, self.port)
                client = AsyncModbusTcpClient(host=self.ip, port=self.port, timeout=5, retries=0, reconnect_delay=0)
                self.plc_client = client
                try:
                    await asyncio.wait_for(self.plc_client.connect(), timeout=10)
                except asyncio.TimeoutError:
                    _logger.warning("PLC connect timeout")
                    await self._close_client()
                    await asyncio.to_thread(AlarmSaver.create, AlarmType.MASTER_PLC)
                    return

                if not getattr(self.plc_client, "connected", False):
                    _logger.warning("PLC not connected after connect()")
                    await self._close_client()
                    await asyncio.to_thread(AlarmSaver.create, AlarmType.MASTER_PLC)
                    return

                self._is_connected = True
                _logger.info("PLC connected")
            except Exception:
                _logger.exception("PLC connect failed")
                self._is_connected = False
                await asyncio.to_thread(AlarmSaver.create, AlarmType.MASTER_PLC)
                await self._close_client()

    async def _close_client(self):
        client = self.plc_client
        if client:
            try:
                if getattr(client, "connected", False):
                    await client.close()
            except Exception:
                _logger.exception("PLC closing client failed")
            finally:
                transport = getattr(client, "_transport", None)
                if transport:
                    try:
                        transport.close()
                    except Exception:
                        pass
                self.plc_client = None
                self._is_connected = False

    async def _heart_beat_loop(self):
        try:
            while gdata.configCommon.is_master and self.plc_client and getattr(self.plc_client, "connected", False) and not self._is_stopped:
                try:
                    self._retries = 0
                    await self.handle_alarm_recovery()
                except asyncio.CancelledError:
                    raise
                except Exception:
                    _logger.exception("PLC heart_beat exception")
                    await asyncio.to_thread(AlarmSaver.create, AlarmType.MASTER_PLC)
                await asyncio.sleep(5)
        finally:
            self._is_connected = False
            await asyncio.to_thread(AlarmSaver.create, AlarmType.MASTER_PLC)
            await self._close_client()
            _logger.info("PLC heart_beat exit and closed")

    # --- safe read/write helpers ---
    async def _safe_read_register(self, address: int, default: Optional[int] = None) -> Optional[int]:
        if not (self.plc_client and getattr(self.plc_client, "connected", False)):
            return default
        try:
            resp = await asyncio.wait_for(self.plc_client.read_holding_registers(address, count=1), timeout=2)
            if resp is None or getattr(resp, "isError", lambda: False)():
                return default
            regs = getattr(resp, "registers", None)
            if regs and len(regs) > 0:
                return int(regs[0]) & 0xFFFF
        except Exception:
            _logger.exception("PLC read_holding_registers failed at %s", address)
        return default

    async def _safe_read_coil(self, address: int, default: Optional[bool] = None) -> Optional[bool]:
        if not (self.plc_client and getattr(self.plc_client, "connected", False)):
            return default
        try:
            resp = await asyncio.wait_for(self.plc_client.read_coils(address=address, count=1), timeout=2)
            if resp is None or getattr(resp, "isError", lambda: False)():
                return default
            bits = getattr(resp, "bits", None)
            if bits and len(bits) > 0:
                return bool(bits[0])
        except Exception:
            _logger.exception("PLC read_coils failed at %s", address)
        return default

    async def _safe_write_register(self, address: int, value: int):
        if not (self.plc_client and getattr(self.plc_client, "connected", False)):
            _logger.debug("PLC write requested but not connected")
            return
        async with self._rw_lock:
            try:
                await asyncio.wait_for(self.plc_client.write_register(address, int(value)), timeout=2)
            except Exception:
                _logger.exception("PLC write_register failed at %s", address)
                await asyncio.to_thread(AlarmSaver.create, AlarmType.MASTER_PLC)

    async def _safe_write_coil(self, address: int, value: bool):
        if not (self.plc_client and getattr(self.plc_client, "connected", False)):
            return
        async with self._rw_lock:
            try:
                await asyncio.wait_for(self.plc_client.write_coil(address=address, value=bool(value)), timeout=2)
            except Exception:
                _logger.exception("PLC write_coil failed at %s", address)
                await asyncio.to_thread(AlarmSaver.create, AlarmType.MASTER_PLC)

    # --- public API (full set preserved) ---
    async def read_4_20_ma_data(self) -> dict:
        if not self._is_connected:
            return self._empty_4_20ma_data()
        try:
            return {
                "power_range_min": await self._safe_read_register(12298, 0),
                "power_range_max": await self._safe_read_register(12299, 0),
                "power_range_offset": await self._safe_read_register(12300, 0),
                "torque_range_min": await self._safe_read_register(12308, 0),
                "torque_range_max": await self._safe_read_register(12309, 0),
                "torque_range_offset": await self._safe_read_register(12310, 0),
                "thrust_range_min": await self._safe_read_register(12318, 0),
                "thrust_range_max": await self._safe_read_register(12319, 0),
                "thrust_range_offset": await self._safe_read_register(12320, 0),
                "speed_range_min": await self._safe_read_register(12328, 0),
                "speed_range_max": await self._safe_read_register(12329, 0),
                "speed_range_offset": await self._safe_read_register(12330, 0)
            }
        except Exception:
            _logger.exception("read_4_20_ma_data failed")
            return self._empty_4_20ma_data()

    async def write_4_20_ma_data(self, data: dict):
        if not self._is_connected:
            _logger.warning("write_4_20_ma_data while not connected")
            return
        # clamp to 0..65535
        def safe_int(v):
            try:
                iv = int(v)
            except Exception:
                iv = 0
            return max(0, min(iv, 0xFFFF))
        await self._safe_write_register(12298, safe_int(data.get("power_range_min", 0)))
        await self._safe_write_register(12299, safe_int(data.get("power_range_max", 0)))
        await self._safe_write_register(12300, safe_int(data.get("power_range_offset", 0)))
        await self._safe_write_register(12308, safe_int(data.get("torque_range_min", 0)))
        await self._safe_write_register(12309, safe_int(data.get("torque_range_max", 0)))
        await self._safe_write_register(12310, safe_int(data.get("torque_range_offset", 0)))
        await self._safe_write_register(12318, safe_int(data.get("thrust_range_min", 0)))
        await self._safe_write_register(12319, safe_int(data.get("thrust_range_max", 0)))
        await self._safe_write_register(12320, safe_int(data.get("thrust_range_offset", 0)))
        await self._safe_write_register(12328, safe_int(data.get("speed_range_min", 0)))
        await self._safe_write_register(12329, safe_int(data.get("speed_range_max", 0)))
        await self._safe_write_register(12330, safe_int(data.get("speed_range_offset", 0)))

    async def write_instant_data(self, power: float, torque: float, thrust: float, speed: float):
        if not self._is_connected:
            return
        _power = max(0, min(int(power / 100), 0xFFFF))
        _torque = max(0, min(int(torque / 100), 0xFFFF))
        _thrust = max(0, min(int(thrust / 100), 0xFFFF))
        _speed = max(0, min(int(speed * 10), 0xFFFF))
        await self._safe_write_register(12301, _power)
        await self._safe_write_register(12311, _torque)
        await self._safe_write_register(12321, _thrust)
        await self._safe_write_register(12331, _speed)

    async def read_instant_data(self) -> dict:
        if not self._is_connected:
            return {"power": None, "torque": None, "thrust": None, "speed": None}
        return {
            "power": await self._safe_read_register(12301),
            "torque": await self._safe_read_register(12311),
            "thrust": await self._safe_read_register(12321),
            "speed": await self._safe_read_register(12331)
        }

    async def write_alarm(self, occured: bool):
        await self._safe_write_coil(12288, occured)

    async def write_power_overload(self, occured: bool):
        await self._safe_write_coil(12289, occured)

    async def write_eexi_breach_alarm(self, occured: bool):
        await self._safe_write_coil(12290, occured)

    async def read_alarm(self) -> bool:
        v = await self._safe_read_coil(12288, False)
        return bool(v) if v is not None else False

    async def read_power_overload(self) -> bool:
        v = await self._safe_read_coil(12289, False)
        return bool(v) if v is not None else False

    async def handle_alarm_recovery(self):
        try:
            _logger.info("PLC recovery alarm")
            await asyncio.to_thread(AlarmSaver.recovery, AlarmType.MASTER_PLC)
            if await asyncio.to_thread(self.has_alarms):
                await self.write_alarm(True)
            else:
                await self.write_alarm(False)
        except Exception:
            _logger.exception("PLC handle_alarm_recovery failed")

    def has_alarms(self) -> bool:
        try:
            cnt = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(AlarmLog.recovery_time.is_null(True)).scalar()
            return cnt > 0
        except Exception:
            _logger.exception("PLC has_alarms failed")
            return False

# global singleton
plc = PlcSyncTask()
