import pynmea2
import flet as ft
from db.models.gps_log import GpsLog
import asyncio
import random


class GpsReadTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.reader = None
        self.writer = None

        self.retries = 0
        self.base_delay = 1   # 基础重连间隔（秒）
        self.retry_backoff = 2  # 退避系数

    async def start(self):
        while True:
            try:
                # 建立连接
                await self.connect()
                # 数据接收循环
                await self.receive_data()
            except (ConnectionRefusedError, ConnectionResetError) as e:
                print(f"连接错误: {e}")
                await self.handle_connection_error()
            except Exception as e:
                print(f"未知错误: {e}")
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
                self.__send_message(
                    f"try to connect...({self.retries+1} times)")

                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection("127.0.0.1", 9527),
                    timeout=5
                )
                self.__send_message("connect success")
                return
            except Exception as e:
                self.__send_message(f"connect failed: {str(e)}")
                self.retries += 1
                await asyncio.sleep(delay)

    async def receive_data(self):
        while not self.reader.at_eof():
            try:
                data = await asyncio.wait_for(
                    self.reader.readline(),
                    timeout=5  # 设置读取超时
                )
                if not data:
                    self.__send_message(
                        "receive empty data, connection may be closed")
                    break

                str_data = data.decode('utf-8').strip()
                self.__send_message(f"receive data: {str_data}")
                self.parse_nmea_sentence(str_data)
            except asyncio.TimeoutError:
                self.__send_message("read timeout, keep connection")
                break
            except Exception as e:
                self.__send_message(f"data receive error: {e}")
                break

    async def handle_connection_error(self):
        self.__send_message("try to reconnect...")
        # 重置重试计数
        self.retries = 0
        await asyncio.sleep(1)

    async def close_connection(self):
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                self.__send_message(f"close connection error: {e}")
            finally:
                self.writer = None
                self.reader = None

    def parse_nmea_sentence(self, sentence):
        try:
            msg = pynmea2.parse(sentence)
            if isinstance(msg, pynmea2.types.talker.RMC):
                utc_date = msg.datestamp
                utc_time = msg.timestamp
                latitude = msg.latitude
                longitude = msg.longitude
                location = f"{longitude},{latitude}"
                self.__set_session('instant_gps_location', location)
                utc_date_time = f"{utc_date} {utc_time}"
                GpsLog.create(location=location, utc_date_time=utc_date_time)
        except pynmea2.ParseError as e:
            self.__send_message(f"parse nmea sentence failed: {e}")
            self.__set_session('instant_gps_location', None)

    def __set_session(self, key: str, value: any):
        self.page.session.set(key, value)

    def __send_message(self, message: str):
        self.page.pubsub.send_all_on_topic('gps_log', message)
