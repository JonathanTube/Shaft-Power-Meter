# gps_sync_task.py (optimized)

import asyncio
import logging
import pynmea2
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from common.const_alarm_type import AlarmType
from db.models.gps_log import GpsLog
from common.global_data import gdata
from db.models.io_conf import IOConf
from utils.alarm_saver import AlarmSaver
from db.models.system_settings import SystemSettings

_logger = logging.getLogger("GpsSyncTask")


class GpsSyncTask:
    def __init__(self):
        self.reader = None
        self.writer = None
        self._lock = asyncio.Lock()
        self._retry = 0
        self._max_retries = 6
        self._is_connected = False
        self._is_canceled = False
        self._task: asyncio.Task | None = None
        self._is_master = False

    @property
    def is_connected(self):
        return self._is_connected

    def start(self):
        """启动任务并返回 asyncio.Task"""
        if self._task and not self._task.done():
            return self._task
        self._task = asyncio.create_task(self.connect(), name="gps-connect")
        return self._task

    async def stop(self):
        """安全停止"""
        self._is_canceled = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.close()

    async def connect(self):
        system_settings: SystemSettings = await asyncio.to_thread(SystemSettings.get)
        self._is_master = system_settings.is_master

        async with self._lock:
            self._retry = 0
            self._is_canceled = False

            while self._retry < self._max_retries and not self._is_canceled:
                try:
                    io_conf: IOConf = await asyncio.to_thread(IOConf.get)
                    _logger.info(f"[GPS] Connecting ({self._retry+1}) {io_conf.gps_ip}:{io_conf.gps_port}")
                    self.reader, self.writer = await asyncio.wait_for(
                        asyncio.open_connection(io_conf.gps_ip, io_conf.gps_port),
                        timeout=5
                    )
                    _logger.info("[GPS] Connected")
                    await self._receive_loop()
                    _logger.info("[GPS] Disconnected (loop ended)")
                except (ConnectionError, TimeoutError, asyncio.CancelledError):
                    if not self._is_canceled:
                        _logger.exception("[GPS] connect/read error")
                        await asyncio.to_thread(
                            AlarmSaver.create,
                            AlarmType.MASTER_GPS if self._is_master else AlarmType.SLAVE_GPS
                        )
                except Exception:
                    _logger.exception("[GPS] unexpected error")
                finally:
                    self._retry += 1
                    if not self._is_canceled:
                        await asyncio.sleep(min(2 ** self._retry, 30))  # backoff

    async def _receive_loop(self):
        if self.reader is None:
            return
        no_data = 0
        has_data_counter = 0
        while not self.reader.at_eof() and not self._is_canceled:
            try:
                data = await asyncio.wait_for(self.reader.readline(), timeout=5)
                if not data:
                    no_data += 1
                    if no_data > 5:
                        break
                    continue
                no_data = 0
                has_data_counter += 1
                self._is_connected = True
                if has_data_counter % 5 == 0:
                    await asyncio.to_thread(
                        AlarmSaver.recovery,
                        AlarmType.MASTER_GPS if self._is_master else AlarmType.SLAVE_GPS
                    )

                line = data.decode("utf-8", errors="ignore").strip()
                await asyncio.to_thread(self.parse_nmea_sentence, line)
                self._retry = 0
            except asyncio.CancelledError:
                raise
            except Exception:
                _logger.exception("[GPS] exception in receive loop")
                self._is_connected = False
                await asyncio.to_thread(
                    AlarmSaver.create,
                    AlarmType.MASTER_GPS if self._is_master else AlarmType.SLAVE_GPS
                )
                break

    async def close(self):
        self._is_canceled = True
        if self.writer and not self.writer.is_closing():
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                _logger.exception("[GPS] close error")
        self.reader = None
        self.writer = None
        self._is_connected = False

    def parse_nmea_sentence(self, sentence: str):
        """运行在线程池里，避免阻塞事件循环"""
        try:
            gdata.configGps.raw_data = sentence
            # delete old logs (3 months+)
            cutoff = gdata.configDateTime.utc - timedelta(weeks=12)
            GpsLog.delete().where(GpsLog.utc_date_time < cutoff).execute()

            msg = pynmea2.parse(sentence)
            if isinstance(msg, pynmea2.types.talker.RMC):
                utc_date = msg.datestamp
                utc_time = msg.timestamp
                lat_deg = int(msg.latitude)
                lat_min = (msg.latitude - lat_deg) * 60
                lat_str = f"{lat_deg}°{lat_min:.3f}′{msg.lat_dir}"
                lon_deg = int(msg.longitude)
                lon_min = (msg.longitude - lon_deg) * 60
                lon_str = f"{lon_deg}°{lon_min:.3f}′{msg.lon_dir}"
                location = f"{lat_str}, {lon_str}"
                gdata.configGps.location = location
                time_str = f"{utc_date} {utc_time}"
                GpsLog.create(location=location, utc_date_time=time_str)
                if gdata.configDateTime.sync_with_gps:
                    dt = datetime.fromisoformat(time_str)
                    dt_utc = dt.astimezone(ZoneInfo("UTC")).replace(microsecond=0, tzinfo=None)
                    gdata.configDateTime.utc = dt_utc
        except Exception:
            _logger.exception("[GPS] parse failed")


gps = GpsSyncTask()
