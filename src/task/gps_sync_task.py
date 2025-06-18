from datetime import datetime, timedelta
import logging
from zoneinfo import ZoneInfo
import pynmea2
from common.const_alarm_type import AlarmType
from db.models.gps_log import GpsLog
import asyncio
import random
from common.global_data import gdata
from db.models.io_conf import IOConf
from utils.alarm_saver import AlarmSaver


class GpsSyncTask:
    def __init__(self):
        self.reader = None
        self.writer = None

        self.running = False
        self.retries = 0
        self.base_delay = 1   # 基础重连间隔（秒）
        self.retry_backoff = 2  # 退避系数
        self._lock = asyncio.Lock()

    async def start(self, retry_once: bool = False):
        self.running = True
        while self.running:
            # 建立连接
            await self.connect(retry_once)
            try:
                if gdata.connected_to_gps:
                    # 数据接收循环
                    await self.receive_data()
                if retry_once:
                    return
            except (TimeoutError, ConnectionRefusedError, ConnectionResetError) as e:
                logging.error(f"[***GPS***]gps connection error")
                await self.handle_connection_error()
                gdata.connected_to_gps = False
            except Exception as e:
                logging.error(f"[***GPS***]gps unknown error")
                await self.handle_connection_error()
            finally:
                gdata.connected_to_gps = False

    async def connect(self, retry_once: bool):
        async with self._lock:  # 确保单线程重连
            self.retries = 0
            while self.running:
                try:
                    # 使用指数退避算法
                    delay = self.base_delay * \
                        (self.retry_backoff ** self.retries)

                    io_conf: IOConf = IOConf.get()
                    logging.info(
                        f'[***GPS***]connecting to gps, ip={io_conf.gps_ip}, port={io_conf.gps_port}')

                    self.reader, self.writer = await asyncio.wait_for(
                        asyncio.open_connection(
                            io_conf.gps_ip, io_conf.gps_port),
                        timeout=5
                    )

                    gdata.connected_to_gps = True
                    logging.info(
                        f'[***GPS***]connected to gps, ip={io_conf.gps_ip}, port={io_conf.gps_port}')
                    AlarmSaver.recovery(alarm_type=AlarmType.GPS_DISCONNECTED)
                    # 这里需要return,不然死循环
                    return
                except (ConnectionRefusedError, ConnectionResetError):
                    if retry_once:
                        return
                    logging.error(f"[***GPS***]connect to gps timeout, retry times={self.retries}, retry after {delay} seconds")
                    self.retries += 1
                    gdata.connected_to_gps = False
                    AlarmSaver.create(alarm_type=AlarmType.GPS_DISCONNECTED)
                    await asyncio.sleep(delay)

    async def receive_data(self):
        timeout_count = 0
        while not self.reader.at_eof() and self.running:
            try:
                data = await asyncio.wait_for(self.reader.readline(), timeout=5)
                if not data:
                    continue

                str_data = data.decode('utf-8').strip()
                self.parse_nmea_sentence(str_data)
            except asyncio.TimeoutError:
                timeout_count += 1
                if timeout_count > 3:  # 连续3次超时视为断连
                    logging.error(
                        f"[***GPS***] after 3 times timeout, reconnect...")
                    self.running = False
                    AlarmSaver.create(AlarmType.GPS_DISCONNECTED)
                    raise ConnectionAbortedError()
            except (ConnectionResetError, ConnectionAbortedError) as e:
                logging.error(f"[***GPS***] Connection lost: {e}")
                AlarmSaver.create(AlarmType.GPS_DISCONNECTED)
                raise ConnectionAbortedError()  # 触发重连
            except Exception:
                logging.error("[***GPS***]gps data receive error")

    async def handle_connection_error(self):
        # 重置重试计数
        self.retries = 0
        await asyncio.sleep(1)

    async def close_connection(self):
        self.running = False
        logging.info(f'[***GPS***]disconnected from GPS')
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                logging.error("[***GPS***]gps close connection error")
            finally:
                self.writer = None
                self.reader = None
                AlarmSaver.create(AlarmType.GPS_DISCONNECTED)

    def parse_nmea_sentence(self, sentence):
        try:
            gdata.gps_raw_data = sentence
            # delete invalid data(4 weeks * 3 = 12 weeks ago)
            GpsLog.delete().where(GpsLog.utc_date_time < (
                gdata.utc_date_time - timedelta(weeks=4 * 3))).execute()
            msg = pynmea2.parse(sentence)
            if isinstance(msg, pynmea2.types.talker.RMC):
                utc_date = msg.datestamp
                utc_time = msg.timestamp
                latitude = msg.latitude
                longitude = msg.longitude
                location = f"{longitude},{latitude}"
                gdata.gps_location = location
                time_str = f"{utc_date} {utc_time}"
                GpsLog.create(location=location, utc_date_time=time_str)
                # 更新UTC时间
                if gdata.enable_utc_time_sync_with_gps:
                    dt = datetime.fromisoformat(time_str)
                    # UTC标准化+去除微秒
                    dt_utc = dt.astimezone(ZoneInfo("UTC")).replace(
                        microsecond=0, tzinfo=None)
                    gdata.utc_date_time = dt_utc

        except pynmea2.ParseError:
            logging.error("[***GPS***]gps parse nmea sentence failed")
            gdata.gps_location = None


gps_sync_task = GpsSyncTask()
