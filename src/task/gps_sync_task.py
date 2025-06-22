import logging
import asyncio
import pynmea2
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from common.const_alarm_type import AlarmType
from db.models.gps_log import GpsLog
from common.global_data import gdata
from db.models.io_conf import IOConf
from utils.alarm_saver import AlarmSaver


class GpsSyncTask:
    def __init__(self):
        self.reader = None
        self.writer = None

        self._lock = asyncio.Lock()

        self._max_retries = 20  # 最大重连次数

        self._is_connected = False

        self._is_canceled = False

    @property
    def is_connected(self):
        return self._is_connected

    async def connect(self):
        retry = 0
        async with self._lock:  # 确保单线程重连
            while retry < self._max_retries:
                if self._is_canceled:
                    break

                if self._is_connected:
                    break

                try:
                    io_conf: IOConf = IOConf.get()

                    logging.info(f'[***GPS***]connecting to gps, ip={io_conf.gps_ip}, port={io_conf.gps_port}')
                    self.reader, self.writer = await asyncio.wait_for(
                        asyncio.open_connection(io_conf.gps_ip, io_conf.gps_port),
                        timeout=10
                    )

                    logging.info(f'[***GPS***]connected to gps, ip={io_conf.gps_ip}, port={io_conf.gps_port}')

                    # 连接成功
                    self._is_connected = True
                    AlarmSaver.recovery(alarm_type=AlarmType.GPS_DISCONNECTED)

                    await self.receive_data()

                    logging.info(f'[***GPS***]disconnected from gps, ip={io_conf.gps_ip}, port={io_conf.gps_port}')
                    # 执行到这了，说明已经退出了
                    # 如果是手动取消，直接跳出
                    if self._is_canceled:
                        break
                    # 否则进入下一次循环
                except:
                    logging.error(f"[***GPS***]connect to gps timeout, retry times={retry + 1}")
                    self._is_connected = False
                    AlarmSaver.create(alarm_type=AlarmType.GPS_DISCONNECTED)
                finally:
                    #  指数退避
                    await asyncio.sleep(2 ** retry)
                    retry += 1

            # 重新设置为未取消，准备下一次链接
            self._is_canceled = False

    async def receive_data(self):
        while not self.reader.at_eof():
            if self._is_canceled:
                break

            try:
                data = await asyncio.wait_for(self.reader.readline(), timeout=10)
                if not data:
                    continue

                str_data = data.decode('utf-8').strip()
                self.parse_nmea_sentence(str_data)
            except:
                self._is_connected = False
                AlarmSaver.create(AlarmType.GPS_DISCONNECTED)
                break

    async def close(self):
        logging.info(f'[***GPS***] disconnected from GPS')
        try:
            if not self.writer.is_closing():
                self.writer.close()
                await self.writer.wait_closed()
        except:
            logging.error("[***GPS***] gps close connection error")
        finally:
            self.writer = None
            self.reader = None
            self._is_connected = False
            self._is_canceled = True
            AlarmSaver.create(AlarmType.GPS_DISCONNECTED)

    def parse_nmea_sentence(self, sentence):
        try:
            gdata.gps_raw_data = sentence
            # delete invalid data(4 weeks * 3 = 12 weeks ago)
            GpsLog.delete().where(GpsLog.utc_date_time < (gdata.utc_date_time - timedelta(weeks=4 * 3))).execute()
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
        except:
            logging.exception("[***GPS***]gps parse nmea sentence failed")
            gdata.gps_location = None


gps = GpsSyncTask()
