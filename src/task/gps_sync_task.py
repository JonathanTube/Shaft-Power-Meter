import asyncio
import logging
import pynmea2
from zoneinfo import ZoneInfo
from datetime import datetime
from common.const_alarm_type import AlarmType
from db.models.gps_log import GpsLog
from common.global_data import gdata
from utils.alarm_saver import AlarmSaver

_logger = logging.getLogger("GpsSyncTask")


class GpsSyncTask:
    def __init__(self):
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None
        self.is_online = False  # TCP连接状态
        self.is_canceled = False

    @property
    def is_connected(self) -> bool:
        return self.writer is not None and not self.writer.is_closing()

    async def start(self):
        self.is_canceled = False
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._run(), name="gps-task")
        return self._task

    async def stop(self):
        _logger.info("[GPS] 停止任务")
        self.is_canceled = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.close()
        await self.set_offline()

    async def _run(self):
        while not self.is_canceled:
            try:
                ok = await self.connect()
                if ok:
                    await self._receive_loop()
            except asyncio.CancelledError:
                break
            except Exception:
                _logger.exception("[GPS] 运行异常")

            # 确保清理
            await self.close()
            await self.set_offline()

            # 3 秒后重连
            if not self.is_canceled:
                _logger.info("[GPS] 10 秒后重试连接...")
                await asyncio.sleep(10)

    async def connect(self) -> bool:
        async with self._lock:
            gps_ip = gdata.configIO.gps_ip
            gps_port = gdata.configIO.gps_port
            _logger.info(f"[GPS] 尝试连接 {gps_ip}:{gps_port}")
            try:
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(gps_ip, gps_port), timeout=5
                )
                await self.set_online()
                _logger.info("[GPS] 连接成功")
                return True
            except Exception as e:
                _logger.warning(f"[GPS] 连接失败: {e}")
                return False

    async def _receive_loop(self):
        while self.is_connected:
            try:
                line = await asyncio.wait_for(self.reader.readline(), timeout=5)
                if not line:
                    _logger.warning("[GPS] 连接关闭")
                    break
                await asyncio.to_thread(self.parse_nmea_sentence, line.decode("utf-8", "ignore").strip())
            except asyncio.TimeoutError:
                continue
            except (asyncio.IncompleteReadError, ConnectionResetError):
                _logger.warning("[GPS] 连接被重置")
                break
            except asyncio.CancelledError:
                raise
            except Exception:
                _logger.exception("[GPS] 接收异常")
                break

    async def close(self):
        if self.writer and not self.writer.is_closing():
            try:
                self.writer.close()
            except Exception:
                _logger.exception("[GPS] 关闭异常")
        self.reader = self.writer = None

    def parse_nmea_sentence(self, sentence: str):
        try:
            gdata.configGps.raw_data = sentence
            msg = pynmea2.parse(sentence)
            if isinstance(msg, pynmea2.types.talker.RMC):
                lat_deg = int(msg.latitude)
                lat_min = (msg.latitude - lat_deg) * 60
                lon_deg = int(msg.longitude)
                lon_min = (msg.longitude - lon_deg) * 60
                location = f"{lat_deg}°{lat_min:.3f}′{msg.lat_dir}, {lon_deg}°{lon_min:.3f}′{msg.lon_dir}"
                gdata.configGps.location = location
                time_str = f"{msg.datestamp} {msg.timestamp}"
                GpsLog.create(location=location, utc_date_time=time_str)
                if gdata.configDateTime.sync_with_gps:
                    dt = datetime.fromisoformat(time_str)
                    gdata.configDateTime.utc = dt.astimezone(ZoneInfo("UTC")).replace(microsecond=0, tzinfo=None)
        except Exception:
            _logger.exception("[GPS] 解析失败")

    async def set_online(self):
        self.is_online = True
        await AlarmSaver.recovery(AlarmType.MASTER_GPS)

    async def set_offline(self):
        self.is_online = False
        await AlarmSaver.create(AlarmType.MASTER_GPS)


gps = GpsSyncTask()
