from datetime import datetime, timedelta
import logging
from zoneinfo import ZoneInfo
import pynmea2
import flet as ft
from common.const_alarm_type import AlarmType
from db.models.gps_log import GpsLog
import asyncio
import random
from common.global_data import gdata
from utils.alarm_saver import AlarmSaver


class GpsSyncTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.reader = None
        self.writer = None

        self.retries = 0
        self.base_delay = 1   # 基础重连间隔（秒）
        self.retry_backoff = 2  # 退避系数

    async def start(self):
        while True:
            # 建立连接
            await self.connect()
            try:
                # 数据接收循环
                await self.receive_data()
            except (ConnectionRefusedError, ConnectionResetError) as e:
                logging.error(f"gps connection error: {e}")
                await self.handle_connection_error()
            except Exception as e:
                logging.error(f"gps unknown error: {e}")
                await self.handle_connection_error()
            finally:
                await self.close_connection()

    async def connect(self):
        self.retries = 0
        while True:
            try:
                # 使用指数退避算法
                delay = self.base_delay * (self.retry_backoff ** self.retries)
                delay += random.uniform(0, 1)  # 添加随机抖动

                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(gdata.gps_ip, gdata.gps_port),
                    timeout=5
                )

                return
            except Exception as e:
                logging.error(f"gps connect error: {e}")
                self.retries += 1
                AlarmSaver.create(AlarmType.GPS_DISCONNECTED)
                await asyncio.sleep(delay)

    async def receive_data(self):
        while not self.reader.at_eof():
            try:
                data = await asyncio.wait_for(self.reader.readline(), timeout=5)
                if not data:
                    break

                str_data = data.decode('utf-8').strip()
                self.parse_nmea_sentence(str_data)
            except asyncio.TimeoutError:
                logging.error("gps receive data timeout, keep connection")
                break
            except Exception as e:
                logging.error(f"gps data receive error: {e}")
                break

    async def handle_connection_error(self):
        # 重置重试计数
        self.retries = 0
        await asyncio.sleep(1)

    async def close_connection(self):
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                logging.error(f"gps close connection error: {e}")
            finally:
                self.writer = None
                self.reader = None

    def parse_nmea_sentence(self, sentence):
        try:
            # delete invalid data(4 weeks * 3 = 12 weeks ago)
            GpsLog.delete().where(GpsLog.utc_date_time < (gdata.utc_date_time - timedelta(weeks=4 * 3)))
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
                    dt_utc = dt.astimezone(ZoneInfo("UTC")).replace(microsecond=0, tzinfo=None)
                    gdata.utc_date_time = dt_utc

        except pynmea2.ParseError as e:
            logging.error(f"gps parse nmea sentence failed: {e}")
            gdata.gps_location = None
