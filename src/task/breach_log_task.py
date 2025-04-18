import flet as ft
import asyncio
from common.global_data import gdata
from db.models.event_log import EventLog
from db.models.system_settings import SystemSettings
from db.models.report_info import ReportInfo
from db.models.report_detail import ReportDetail
from utils.formula_cal import FormulaCalculator
from task.utc_timer_task import utc_timer


class BreachLogTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.start_time = None
        self.event_log_id = None
        self.breach_times = 0
        self.recovery_times = 0
        self.report_info = None
        self.checking_continuous_interval = 60

    async def start(self):
        system_settings = SystemSettings.get()
        # 功率必须突破EEXI持续超过60s后，才算突破
        self.checking_continuous_interval = system_settings.eexi_breach_checking_duration
        eexi_limited_power = system_settings.eexi_limited_power
        while True:
            if system_settings.sha_po_li == False:
                break

            sps1_instant_power = self.__get_session("sps1_instant_power") or 0
            sps2_instant_power = self.__get_session("sps2_instant_power") or 0

            if sps1_instant_power is None or sps2_instant_power is None or eexi_limited_power is None:
                await asyncio.sleep(1)
                continue

            # 功率突破EEXI限制
            instant_power = sps1_instant_power + sps2_instant_power
            # print("instant_power=", instant_power)
            # print("eexi_limited_power=", eexi_limited_power)
            if instant_power > eexi_limited_power:
                self.__handle_breach_event()
            else:
                self.__handle_recovery_event()
            await asyncio.sleep(1)

    def __handle_breach_event(self):
        self.breach_times += 1
        print(f"breach_times: {self.breach_times}")
        # 没有记录开始时间，则记录突破-开始时间
        if self.start_time is None:
            self.start_time = self.__get_utc_date_time()
            return

        # 连续突破60s，则记录突破事件
        if self.breach_times == self.checking_continuous_interval:
            started_position = self.__get_instant_gps_location()
            event_log: EventLog = EventLog.create(
                started_at=self.start_time, started_position=started_position)

            self.report_info = ReportInfo.create(
                event_log=event_log, report_name=f"Compliance Report #{event_log.id}")
            self.event_log_id = event_log.id
            gdata.breach_eexi_occured = True
            gdata.alarm_occured = True
            gdata.power_overload_occured = True

        if self.breach_times > self.checking_continuous_interval:
            self.__record_report_detail()

    def __record_report_detail(self):
        if self.report_info is None:
            return

        utc_date_time = self.__get_utc_date_time()
        speed = self.__get_session("sps1_instant_speed") or 0
        torque = self.__get_session("sps1_instant_torque") or 0
        power = self.__get_session("sps1_instant_power") or 0
        total_power = FormulaCalculator.calculate_energy_kwh(power)

        ReportDetail.create(
            report_info=self.report_info,
            utc_date_time=utc_date_time,
            speed=speed,
            torque=torque,
            power=power,
            total_power=total_power
        )

    def __handle_recovery_event(self):
        if self.event_log_id is None:
            return
        # print(f"recovery_times: {self.recovery_times}")
        if self.breach_times < self.checking_continuous_interval:
            self.__reset_all()
            return

        self.recovery_times += 1
        if self.recovery_times == self.checking_continuous_interval:
            # print("self.event_log_id=", self.event_log_id)
            event_log = EventLog.get(self.event_log_id)
            event_log.ended_at = self.__get_utc_date_time()
            event_log.ended_position = self.__get_instant_gps_location()
            event_log.save()
            self.__reset_all()
            gdata.breach_eexi_occured = False
            gdata.alarm_occured = False
            gdata.power_overload_occured = False

        if self.recovery_times <= self.checking_continuous_interval:
            self.__record_report_detail()

    def __reset_all(self):
        self.breach_times = 0
        self.recovery_times = 0
        self.start_time = None
        self.event_log_id = None
        self.report_info = None

    def __get_utc_date_time(self):
        return utc_timer.get_utc_date_time()

    def __get_instant_gps_location(self):
        return self.__get_session("instant_gps_location")

    def __get_session(self, key: str):
        return self.page.session.get(key)
