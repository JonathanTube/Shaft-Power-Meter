from common.global_data import gdata
from common.control_manager import ControlManager
from db.models.event_log import EventLog
from db.models.report_detail import ReportDetail
from db.models.report_info import ReportInfo
from datetime import timedelta, datetime
from db.models.data_log import DataLog
from db.models.system_settings import SystemSettings
from utils.formula_cal import FormulaCalculator
from peewee import fn
import logging


class EEXIBreach:
    report_id = None

    @staticmethod
    def handle_breach_and_recovery():
        # logging.info('==================eexi_breach_task: start==================')
        system_settings: SystemSettings = SystemSettings.get()
        is_enable = system_settings.sha_po_li
        if not is_enable:
            return

        # 如果正在突破，则保存突破报告明细
        if EEXIBreach.report_id is not None:
            EEXIBreach.__save_report_detail('sps1', gdata.utc_date_time, gdata.sps1_speed, gdata.sps1_torque, gdata.sps1_power)
            # 如果是双桨，则保存双桨的报告明细
            is_twins = system_settings.amount_of_propeller == 2
            if is_twins:
                EEXIBreach.__save_report_detail('sps2', gdata.utc_date_time, gdata.sps2_speed, gdata.sps2_torque, gdata.sps2_power)

        seconds = system_settings.eexi_breach_checking_duration
        eexi_limited_power = system_settings.eexi_limited_power
        start_time = gdata.utc_date_time - timedelta(seconds=seconds)

        # 再减去数据刷新间隔，类似滑动窗口，因为下位机数据采集间隔是1s，所以需要减去1s
        start_time = start_time - timedelta(seconds=1)

        # 查找时间窗口内的功率记录
        data: list[DataLog] = EEXIBreach.__query_data_in_time_window(start_time)

        if len(data) == 0:
            return

        if EEXIBreach.__is_invalid_seconds_diff(data, seconds):
            return

        # 计算过载次数
        breach_times = sum(1 for item in data if item.power > eexi_limited_power)
        if breach_times == len(data):
            logging.info(f"eexi_breach_checking_duration = {seconds}s")
            logging.info(f"start_time = {gdata.utc_date_time} - {seconds}s = {start_time}")
            logging.info(f"start_time = {gdata.utc_date_time} - {seconds}s - 1s = {start_time}")
            logging.info(f"breach_times = {breach_times}")
            EEXIBreach.__handle_breach_event(start_time)

        # 计算恢复次数
        recovery_times = sum(1 for item in data if item.power <= eexi_limited_power)
        if recovery_times == len(data):
            logging.info(f"eexi_breach_checking_duration = {seconds}s")
            logging.info(f"start_time = {gdata.utc_date_time} - {seconds}s = {start_time}")
            logging.info(f"start_time = {gdata.utc_date_time} - {seconds}s - 1s = {start_time}")
            logging.info(f"recovery_times = {recovery_times}")
            EEXIBreach.__handle_recovery_event(start_time)
        # logging.info('==================eexi_breach_task: end==================\n')

    @staticmethod
    def __is_invalid_seconds_diff(data, seconds) -> bool:
        # 计算时间差，如果时间差小于60s，则不进行处理
        start_time: datetime = data[0].utc_date_time
        # logging.info(f"start_time of data list = {start_time}")
        end_time: datetime = data[-1].utc_date_time
        # logging.info(f"end_time of data list = {end_time}")
        time_diff = abs(end_time - start_time)
        # logging.info(f"time_diff = {time_diff.total_seconds()}s")
        return time_diff.total_seconds() < seconds

    @staticmethod
    def __query_data_in_time_window(start_time: datetime) -> list[DataLog]:
        data = DataLog.select(
            DataLog.utc_date_time,
            fn.sum(DataLog.power).alias("power")
        ).where(
            DataLog.utc_date_time >= start_time
        ).group_by(
            DataLog.utc_date_time
        ).order_by(
            DataLog.utc_date_time.asc()
        )
        # logging.info(f"data.length = {len(data)}")
        return data

    @staticmethod
    def __handle_breach_event(start_time: datetime):
        # 如果还没有创建报告，则创建报告
        if EEXIBreach.report_id is None:

            ControlManager.audio_alarm.play()
            ControlManager.fullscreen_alert.start()
            if ControlManager.event_button is not None:
                ControlManager.event_button.update_event()

            event_log: EventLog = EventLog.create(started_at=start_time, started_position=gdata.gps_location)

            report_info = ReportInfo.create(event_log=event_log, report_name=f"Compliance Report #{event_log.id}")

            EEXIBreach.report_id = report_info.id
            # 记录之前所有的过载数据
            data = DataLog.select(
                DataLog.name,
                DataLog.utc_date_time,
                DataLog.speed,
                DataLog.ad_0_torque,
                DataLog.power
            ).where(
                DataLog.utc_date_time >= start_time
            ).order_by(DataLog.utc_date_time.asc())
            for item in data:
                EEXIBreach.__save_report_detail(item.name, item.utc_date_time, item.speed, item.torque, item.power)

    @staticmethod
    def __handle_recovery_event(start_time: datetime):
        if EEXIBreach.report_id is not None:
            ControlManager.audio_alarm.stop()
            ControlManager.fullscreen_alert.stop()
            event_log: EventLog = EventLog.select().where(EventLog.ended_at == None).order_by(EventLog.id.asc()).first()

            if event_log is not None:
                event_log.ended_at = gdata.utc_date_time
                event_log.ended_position = gdata.gps_location
                event_log.save()

            EEXIBreach.report_id = None
            # 记录之前所有的恢复数据
            data = DataLog.select(
                DataLog.name, DataLog.utc_date_time, DataLog.speed, DataLog.ad_0_torque, DataLog.power
            ).where(
                DataLog.utc_date_time >= start_time
            ).order_by(DataLog.utc_date_time.asc())
            for item in data:
                EEXIBreach.__save_report_detail(item.name, item.utc_date_time, item.speed, item.torque, item.power)

    @staticmethod
    def __save_report_detail(name: str, utc_date_time: datetime, speed: float, torque: float, power: float):
        # print(f"EEXIBreach.__save_report_detail: {name}, {utc_date_time}, {speed}, {torque}, {power}")
        try:
            # print(f"EEXIBreach.report_id: {EEXIBreach.report_id}")
            report_info = ReportInfo.get_or_none(ReportInfo.id == EEXIBreach.report_id)
            # print(f"report_info: {report_info}")
            if report_info is None:
                return
            total_power = FormulaCalculator.calculate_energy_kwh(power)
            # save each 15 seconds for reducing the the amount of data
            if utc_date_time.second % 15 == 0:
                ReportDetail.create(
                    report_info=report_info,
                    name=name,
                    utc_date_time=utc_date_time,
                    speed=speed,
                    torque=torque,
                    power=power,
                    total_power=total_power
                )
        except Exception as e:
            logging.error(f"save eexi breach report detail error: {e}")
