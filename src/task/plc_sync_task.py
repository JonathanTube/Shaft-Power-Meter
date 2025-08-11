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
        self._lock = asyncio.Lock()  # protect write/read sequences
        self.plc_client: Optional[AsyncModbusTcpClient] = None

        self._keepalive_task: Optional[asyncio.Task] = None
        self._connect_lock = asyncio.Lock()  # ensure single connect at time

        self._is_connected = False
        self._is_stopped = False

        # reconnect/backoff policy
        self._retries = 0
        self._max_backoff = 32  # seconds

        # local cached address/port
        self.ip = None
        self.port = None

    # ---- Public API ----
    def start(self):
        """Start the keepalive loop (idempotent)."""
        if self._keepalive_task and not self._keepalive_task.done():
            return
        self._is_stopped = False
        self._keepalive_task = asyncio.create_task(self._keepalive_loop(), name="plc-keepalive")

    async def stop(self):
        """Stop keepalive and close client."""
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

    # ---- internal helpers ----
    async def _keepalive_loop(self):
        """Top-level loop: ensure one connect -> heart_beat -> on failure reconnect."""
        backoff = 1
        while gdata.configCommon.is_master and not self._is_stopped:
            try:
                await self._connect_once()
                if self.plc_client and self.plc_client.connected:
                    # reset backoff
                    self._retries = 0
                    backoff = 1
                    await self._heart_beat_loop()
                else:
                    _logger.warning("[PLC] connect_once reported not connected")
            except asyncio.CancelledError:
                break
            except Exception as e:
                _logger.exception("[PLC] unexpected error in keepalive_loop: %s", e)
                AlarmSaver.create(AlarmType.MASTER_PLC)

            # exponential backoff on failure
            wait = min(backoff, self._max_backoff)
            _logger.info("[PLC] waiting %s seconds before reconnect", wait)
            await asyncio.sleep(wait)
            backoff *= 2
            self._retries += 1

        _logger.info("[PLC] keepalive loop exited")

    async def _connect_once(self):
        """Establish a single connection attempt (cleans previous connection first)."""
        async with self._connect_lock:
            await self._close_client()  # ensure previous client fully closed

            try:
                io_conf: IOConf = IOConf.get()
                self.ip = io_conf.plc_ip
                self.port = io_conf.plc_port

                _logger.info(f"[PLC] connecting to {self.ip}:{self.port}")

                # create client and try connecting with timeout
                client = AsyncModbusTcpClient(
                    host=self.ip,
                    port=self.port,
                    timeout=5,
                    retries=0,            # manage retries ourselves
                    reconnect_delay=0
                )
                self.plc_client = client

                # connect() may be a coroutine or return immediately depending on implementation,
                # use wait_for to bound the connect operation
                try:
                    await asyncio.wait_for(self.plc_client.connect(), timeout=10)
                except asyncio.TimeoutError:
                    _logger.warning("[PLC] connect timeout")
                    await self._close_client()
                    AlarmSaver.create(AlarmType.MASTER_PLC)
                    return

                if not self.plc_client.connected:
                    _logger.warning("[PLC] client reports not connected after connect()")
                    await self._close_client()
                    AlarmSaver.create(AlarmType.MASTER_PLC)
                    return

                self._is_connected = True
                _logger.info("[PLC] connected successfully")
            except Exception:
                _logger.exception("[PLC] connect failed")
                self._is_connected = False
                AlarmSaver.create(AlarmType.MASTER_PLC)
                await self._close_client()

    async def _close_client(self):
        """Safely close and drop current client if exists."""
        if self.plc_client:
            try:
                if getattr(self.plc_client, "connected", False):
                    await self.plc_client.close()
            except Exception:
                _logger.exception("[PLC] error closing client")
            finally:
                # ensure underlying resources are freed
                try:
                    # some implementations may provide transport attribute
                    transport = getattr(self.plc_client, "_transport", None)
                    if transport:
                        try:
                            transport.close()
                        except Exception:
                            pass
                except Exception:
                    pass
                self.plc_client = None
                self._is_connected = False

    async def _heart_beat_loop(self):
        """Run periodic tasks while connected."""
        try:
            while gdata.configCommon.is_master and self.plc_client and self.plc_client.connected and not self._is_stopped:
                try:
                    # reset counters
                    self._retries = 0
                    await self.handle_alarm_recovery()
                except asyncio.CancelledError:
                    raise
                except Exception:
                    _logger.exception("[PLC] exception occured in heart_beat")
                    AlarmSaver.create(AlarmType.MASTER_PLC)
                await asyncio.sleep(5)
        finally:
            # connection likely lost
            self._is_connected = False
            AlarmSaver.create(AlarmType.MASTER_PLC)
            await self._close_client()
            _logger.info("[PLC] heart_beat loop exit, connection closed")

    # ---- read/write helpers (safe) ----
    async def _safe_read_register(self, address: int) -> Optional[int]:
        if not (self.plc_client and getattr(self.plc_client, "connected", False)):
            return None
        try:
            # depending on pymodbus version signature may differ
            resp = await self.plc_client.read_holding_registers(address, count=1)
            if resp is None or getattr(resp, "isError", lambda: False)():
                return None
            regs = getattr(resp, "registers", None)
            if regs and len(regs) > 0:
                val = int(regs[0]) & 0xFFFF
                return val
        except Exception:
            _logger.exception("[PLC] read_holding_registers failed at %s", address)
        return None

    async def _safe_read_coil(self, address: int) -> Optional[bool]:
        if not (self.plc_client and getattr(self.plc_client, "connected", False)):
            return None
        try:
            resp = await self.plc_client.read_coils(address, count=1)
            if resp is None or getattr(resp, "isError", lambda: False)():
                return None
            bits = getattr(resp, "bits", None)
            if bits and len(bits) > 0:
                return bool(bits[0])
        except Exception:
            _logger.exception("[PLC] read_coils failed at %s", address)
        return None

    async def read_4_20_ma_data(self) -> dict:
        if not self._is_connected:
            return self._empty_4_20ma_data()

        try:
            return {
                "power_range_min": await self._safe_read_register(12298) or 0,
                "power_range_max": await self._safe_read_register(12299) or 0,
                "power_range_offset": await self._safe_read_register(12300) or 0,
                "torque_range_min": await self._safe_read_register(12308) or 0,
                "torque_range_max": await self._safe_read_register(12309) or 0,
                "torque_range_offset": await self._safe_read_register(12310) or 0,
                "thrust_range_min": await self._safe_read_register(12318) or 0,
                "thrust_range_max": await self._safe_read_register(12319) or 0,
                "thrust_range_offset": await self._safe_read_register(12320) or 0,
                "speed_range_min": await self._safe_read_register(12328) or 0,
                "speed_range_max": await self._safe_read_register(12329) or 0,
                "speed_range_offset": await self._safe_read_register(12330) or 0
            }
        except Exception:
            _logger.exception("[PLC] read_4_20_ma_data failed")
            return self._empty_4_20ma_data()

    async def write_4_20_ma_data(self, data: dict):
        if not self._is_connected:
            _logger.warning("[PLC] write_4_20_ma_data called while not connected")
            return

        async with self._lock:
            try:
                # ensure integers and bounds (0..65535)
                def safe_int(v):
                    iv = int(v) if v is not None else 0
                    return max(0, min(iv, 0xFFFF))

                await self.plc_client.write_register(12298, safe_int(data.get("power_range_min", 0)))
                await self.plc_client.write_register(12299, safe_int(data.get("power_range_max", 0)))
                await self.plc_client.write_register(12300, safe_int(data.get("power_range_offset", 0)))

                await self.plc_client.write_register(12308, safe_int(data.get("torque_range_min", 0)))
                await self.plc_client.write_register(12309, safe_int(data.get("torque_range_max", 0)))
                await self.plc_client.write_register(12310, safe_int(data.get("torque_range_offset", 0)))

                await self.plc_client.write_register(12318, safe_int(data.get("thrust_range_min", 0)))
                await self.plc_client.write_register(12319, safe_int(data.get("thrust_range_max", 0)))
                await self.plc_client.write_register(12320, safe_int(data.get("thrust_range_offset", 0)))

                await self.plc_client.write_register(12328, safe_int(data.get("speed_range_min", 0)))
                await self.plc_client.write_register(12329, safe_int(data.get("speed_range_max", 0)))
                await self.plc_client.write_register(12330, safe_int(data.get("speed_range_offset", 0)))
            except Exception:
                _logger.exception("[PLC] write_4_20_ma_data failed")
                AlarmSaver.create(AlarmType.MASTER_PLC)

    async def write_instant_data(self, power: float, torque: float, thrust: float, speed: float):
        if not self._is_connected:
            return
        async with self._lock:
            try:
                # convert and clamp to 0..65535
                _power = max(0, min(int(power / 100), 0xFFFF))
                _torque = max(0, min(int(torque / 100), 0xFFFF))
                _thrust = max(0, min(int(thrust / 100), 0xFFFF))
                _speed = max(0, min(int(speed * 10), 0xFFFF))

                _logger.debug("[PLC] write real time data to plc: power=%s torque=%s thrust=%s speed=%s",
                              _power, _torque, _thrust, _speed)

                await self.plc_client.write_register(12301, _power)
                await self.plc_client.write_register(12311, _torque)
                await self.plc_client.write_register(12321, _thrust)
                await self.plc_client.write_register(12331, _speed)
            except Exception:
                _logger.exception("[PLC] write_instant_data failed")

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
        except Exception:
            _logger.exception("[PLC] read_instant_data failed")
            return {"power": None, "torque": None, "thrust": None, "speed": None}

    async def write_alarm(self, occured: bool):
        if not self._is_connected:
            return
        async with self._lock:
            try:
                await self.plc_client.write_coil(address=12288, value=bool(occured))
                _logger.info("[PLC] write alarm: %s", occured)
            except Exception:
                _logger.exception("[PLC] write_alarm failed")

    async def write_power_overload(self, occured: bool):
        if not self._is_connected:
            return
        async with self._lock:
            try:
                await self.plc_client.write_coil(address=12289, value=bool(occured))
                _logger.info("[PLC] write power overload: %s", occured)
            except Exception:
                _logger.exception("[PLC] write_power_overload failed")

    async def write_eexi_breach_alarm(self, occured):
        if not self._is_connected:
            return
        async with self._lock:
            try:
                await self.plc_client.write_coil(address=12290, value=bool(occured))
                _logger.info("[PLC] write eexi breach: %s", occured)
            except Exception:
                _logger.exception("[PLC] write_eexi_breach_alarm failed")

    async def read_alarm(self) -> bool:
        if not self._is_connected:
            return False
        try:
            v = await self._safe_read_coil(12288)
            return bool(v)
        except Exception:
            _logger.exception("[PLC] read_alarm failed")
            return False

    async def read_power_overload(self) -> bool:
        if not self._is_connected:
            return False
        try:
            v = await self._safe_read_coil(12289)
            return bool(v)
        except Exception:
            _logger.exception("[PLC] read_power_overload failed")
            return False

    async def handle_alarm_recovery(self):
        try:
            _logger.info('[PLC] recovery PLC Alarm')
            AlarmSaver.recovery(AlarmType.MASTER_PLC)
            if self.has_alarms():
                await self.write_alarm(True)
            else:
                await self.write_alarm(False)
        except Exception:
            _logger.exception('recovery PLC alarm failed.')

    def has_alarms(self) -> bool:
        try:
            cnt = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(AlarmLog.recovery_time.is_null(True)).scalar()
            return cnt > 0
        except Exception:
            _logger.exception("has_alarms failed")
            return False


# global singleton instance (use `from task.plc_sync_task import plc`)
plc = PlcSyncTask()
