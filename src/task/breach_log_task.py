import flet as ft
import asyncio
from datetime import datetime
from db.models.event_log import EventLog


class BreachLogTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.key_start_time = "eexi_breach_start_time"
        self.key_event_log_id = "eexi_breach_event_log_id"
        self.breach_times = 0
        self.recovery_times = 0
        # 功率必须突破EEXI持续超过60s后，才算突破
        self.checking_continuous_interval = 60

    async def start(self):
        while True:
            instant_power = self.__get_session("instant_power")
            eexi_limited_power = self.__get_session("eexi_limited_power")

            if instant_power is not None and eexi_limited_power is not None:
                # 功率突破EEXI限制
                if instant_power > eexi_limited_power:
                    self.__handle_breach_event()
                else:
                    self.__handle_recovery_event()

            await asyncio.sleep(1)

    def __handle_breach_event(self):
        self.breach_times += 1
        start_time = self.__get_session(self.key_start_time)
        # 没有记录开始时间，则记录突破-开始时间
        if start_time is None:
            utc_date_time = self.__get_utc_date_time()
            self.__set_session(self.key_start_time, utc_date_time)
            return

        # 连续突破60s，则记录突破事件
        if self.breach_times == self.checking_continuous_interval:
            started_position = ""
            event_log = EventLog.create(started_at=start_time,
                                        started_position=started_position)
            self.__set_session(self.key_event_log_id, event_log.id)

    def __handle_recovery_event(self):
        if self.breach_times < self.checking_continuous_interval:
            self.__reset_all()
            return

        self.recovery_times += 1
        if self.recovery_times == self.checking_continuous_interval:
            event_log_id = self.__get_session(self.key_event_log_id)
            event_log = EventLog.get(event_log_id)
            event_log.ended_at = self.__get_utc_date_time()
            event_log.ended_position = ""
            event_log.save()
            self.__reset_all()

    def __reset_all(self):
        self.breach_times = 0
        self.recovery_times = 0
        self.__remove_session(self.key_start_time)
        self.__remove_session(self.key_event_log_id)

    def __get_session(self, key: str):
        return self.page.session.get(key)

    def __set_session(self, key: str, value: any):
        self.page.session.set(key, value)

    def __remove_session(self, key: str):
        self.page.session.remove(key)

    def __get_utc_date_time(self):
        return self.page.session.get('utc_date_time')
