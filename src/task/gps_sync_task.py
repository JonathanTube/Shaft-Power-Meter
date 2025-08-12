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

_logger = logging.getLogger("GpsSyncTask")


class GpsSyncTask:
    def __init__(self):
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()
        self._task: asyncio.Task | None = None
        self.is_online = False  # 正在收发数据
        self.is_canceled = False

    @property
    def is_connected(self) -> bool:
        """底层连接状态"""
        return self.writer is not None and not self.writer.is_closing()

    async def start(self):
        """启动任务"""
        self.is_canceled = False
        if self._task and not self._task.done():
            return self._task
        self._task = asyncio.create_task(self._run(), name="gps-task")
        return self._task

    async def stop(self):
        """安全停止"""
        _logger.info("[GPS] 正在停止")
        self.is_canceled = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.close()
        self.set_offline()
        _logger.info("[GPS] 停止成功")

    async def _run(self):
        """主循环（自动重连）"""
        while not self.is_canceled:
            try:
                ok = await self.connect()
                if ok:
                    await self._receive_loop()
            except asyncio.CancelledError:
                break
            except Exception:
                _logger.exception("[GPS] 运行时异常")
            finally:
                await self.close()
                await asyncio.sleep(3)

    async def connect(self):
        """连接到 GPS"""
        async with self._lock:
            try:
                io_conf: IOConf = await asyncio.to_thread(IOConf.get)
            except IOConf.DoesNotExist:
                _logger.error("[GPS] 未找到 IOConf 配置，跳过连接")
                self.set_offline()
                await asyncio.sleep(5)  # 等待一会再重试
                return False

            _logger.info(f"[GPS] 正在连接 {io_conf.gps_ip}:{io_conf.gps_port}")
            try:
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(io_conf.gps_ip, io_conf.gps_port),
                    timeout=5
                )
                _logger.info(f"[GPS] 连接成功 {io_conf.gps_ip}:{io_conf.gps_port}")
                return True
            except ConnectionRefusedError as e:
                _logger.error(f"[GPS] 连接失败: {e}")
            except Exception as e:
                _logger.error(f"[GPS] 连接失败: {e}")
            self.set_offline()
            return False

    async def _receive_loop(self):
        """接收数据循环（防止并发读取冲突）"""
        while self.is_connected:
            try:
                # 串行读取一行数据，避免并发调用 readuntil()/readline()
                data = await asyncio.wait_for(self.reader.readline(), timeout=5)
                if not data:
                    _logger.warning("[GPS] 检测到服务端关闭连接")
                    self.set_offline()
                    break

                line = data.decode("utf-8", errors="ignore").strip()
                await asyncio.to_thread(self.parse_nmea_sentence, line)
                self.set_online()

            except asyncio.TimeoutError:
                # 超时无数据，不改变在线状态
                continue
            except (asyncio.IncompleteReadError, ConnectionResetError):
                _logger.warning("[GPS] 连接被重置")
                self.set_offline()
                break
            except asyncio.CancelledError:
                raise
            except Exception:
                _logger.exception("[GPS] 接收数据异常")
                self.set_offline()
                break

    async def close(self):
        if self.writer and not self.writer.is_closing():
            try:
                self.writer.close()
                # 不 await wait_closed()
            except Exception:
                _logger.exception("[GPS] 关闭连接时出错")
        self.reader = None
        self.writer = None

    def parse_nmea_sentence(self, sentence: str):
        """解析 NMEA 数据"""
        try:
            gdata.configGps.raw_data = sentence
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
            _logger.exception("[GPS] 解析失败")

    def set_online(self):
        if not self.is_online:
            self.is_online = True
            if gdata.configCommon.is_master:
                AlarmSaver.recovery(AlarmType.MASTER_GPS)
            else:
                AlarmSaver.recovery(AlarmType.SLAVE_GPS)

    def set_offline(self):
        if self.is_online:
            self.is_online = False
            if gdata.configCommon.is_master:
                AlarmSaver.create(AlarmType.MASTER_GPS)
            else:
                AlarmSaver.create(AlarmType.SLAVE_GPS)


gps = GpsSyncTask()
