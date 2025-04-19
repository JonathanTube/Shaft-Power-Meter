import asyncio
from common.const_pubsub_topic import PubSubTopic
from common.global_data import gdata
from db.models.event_log import EventLog
from db.models.system_settings import SystemSettings
from db.models.report_info import ReportInfo
from db.models.report_detail import ReportDetail
from utils.formula_cal import FormulaCalculator
import flet as ft


class EEXIBreachTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.start_time = None
        self.breach_times = 0
        self.recovery_times = 0
        self.report_info = None
        self.checking_continuous_interval = 60

    async def start(self):
        system_settings: SystemSettings = SystemSettings.get()
        gdata.enable_shapoli = system_settings.sha_po_li
        # 功率必须突破EEXI持续超过60s后，才算突破
        self.checking_continuous_interval = system_settings.eexi_breach_checking_duration
        eexi_limited_power = system_settings.eexi_limited_power
        while True:
            # 如果shapoli功能未开启，则不进行功率过载告警
            if gdata.enable_shapoli == False:
                self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_AUDIO, False)
                self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_FULLSCREEN, False)
                self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_BADGE, False)
                await asyncio.sleep(5)
                continue

            sps1_instant_power = gdata.sps1_power
            sps2_instant_power = gdata.sps2_power

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
        # print(f"breach_times: {self.breach_times}")
        # 没有记录开始时间，则记录突破-开始时间
        if self.start_time is None:
            self.start_time = gdata.utc_date_time
            return

        # 连续突破60s，则记录突破事件
        if self.breach_times == self.checking_continuous_interval:
            self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_AUDIO, True)
            self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_FULLSCREEN, True)
            self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_BADGE, True)
            event_log: EventLog = EventLog.create(
                started_at=self.start_time,
                started_position=gdata.gps_location
            )

            self.report_info = ReportInfo.create(
                event_log=event_log,
                report_name=f"Compliance Report #{event_log.id}"
            )

        # 如果功率突破EEXI限制持续超过60s，则记录突破事件明细
        if self.breach_times >= self.checking_continuous_interval:
            self.__record_report_detail()

    def __record_report_detail(self):
        if self.report_info is None:
            return

        utc_date_time = gdata.utc_date_time
        speed = gdata.sps1_speed
        torque = gdata.sps1_torque
        power = gdata.sps1_power
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
        if self.breach_times < self.checking_continuous_interval:
            self.__reset_all()
            return

        self.recovery_times += 1
        if self.recovery_times == self.checking_continuous_interval:
            self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_AUDIO, False)
            self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_FULLSCREEN, False)
            self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_BADGE, False)
            event_log: EventLog = EventLog.select().where(
                EventLog.ended_at == None
            ).order_by(EventLog.id.asc()).first()

            if event_log is not None:
                event_log.ended_at = gdata.utc_date_time
                event_log.ended_position = gdata.gps_location
                event_log.save()
                self.__reset_all()

        if self.recovery_times <= self.checking_continuous_interval:
            self.__record_report_detail()

    def __reset_all(self):
        self.breach_times = 0
        self.recovery_times = 0
        self.start_time = None
        self.report_info = None
