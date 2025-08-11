from common.global_data import gdata
from db.models.event_log import EventLog
from db.models.report_detail import ReportDetail
from db.models.report_info import ReportInfo
from datetime import timedelta, datetime
from db.models.data_log import DataLog
from utils.formula_cal import FormulaCalculator
from peewee import fn, Case
import logging


class EEXIBreach:
    report_id = None

    @staticmethod
    def handle_breach_and_recovery():
        # logging.info('==================eexi_breach_task: start==================')
        if not gdata.configCommon.shapoli:
            return

        utc_date_time = gdata.configDateTime.utc
        is_twins = gdata.configCommon.amount_of_propeller == 2

        # 如果正在突破，则保存突破报告明细
        if EEXIBreach.report_id is not None:
            EEXIBreach.__save_report_detail(
                'sps', utc_date_time,
                gdata.configSPS.speed, gdata.configSPS.torque, gdata.configSPS.power
            )
            # 如果是双桨，则保存双桨的报告明细
            if is_twins:
                EEXIBreach.__save_report_detail(
                    'sps2', utc_date_time,
                    gdata.configSPS2.speed, gdata.configSPS2.torque, gdata.configSPS2.power
                )

        seconds = gdata.configCommon.eexi_breach_checking_duration
        start_time = utc_date_time - timedelta(seconds=seconds)

        # 再减去数据刷新间隔，类似滑动窗口，因为下位机数据采集间隔是1s，所以需要减去1s
        start_time = start_time - timedelta(seconds=1)

        # 查询在时间窗口内，功率小于等于eexi的记录
        count_power_below_eexi = 0

        # 查询在时间窗口内，功率大于eexi的记录数
        count_power_above_eexi = 0

        if not is_twins:
            count_power_below_eexi = (
                DataLog.select(fn.COUNT(DataLog.id))
                .where(
                    DataLog.utc_date_time >= start_time,
                    DataLog.power <= gdata.configCommon.eexi_limited_power
                ).scalar()
            )

            count_power_above_eexi = (
                DataLog.select(fn.COUNT(DataLog.id))
                .where(
                    DataLog.utc_date_time >= start_time,
                    DataLog.power > gdata.configCommon.eexi_limited_power
                ).scalar()
            )
        else:
            limit_power = gdata.configCommon.eexi_limited_power

            query = (
                DataLog.select(fn.SUM(DataLog.power).alias('total_power'))
                .where(DataLog.utc_date_time >= start_time)
                .group_by(DataLog.utc_date_time)
            )

            count_query = (
                query.select(
                    fn.SUM(Case(None, [(query.c.total_power <= limit_power, 1)], 0)).alias('below_count'),
                    fn.SUM(Case(None, [(query.c.total_power > limit_power, 1)], 0)).alias('above_count')
                )
            )

            result = count_query.dicts().get()

            count_power_below_eexi = result['below_count']
            count_power_above_eexi = result['above_count']

        # 如果相等，说明没有数据，跳过所有判断，保持原样
        if count_power_below_eexi == count_power_above_eexi:
            return

        # 功率小于eexi的0条，说明突破
        if count_power_below_eexi == 0:
            EEXIBreach.__handle_breach_event(start_time)

        # 功率大于eexi的0条，说明已经恢复
        if count_power_above_eexi == 0:
            EEXIBreach.__handle_recovery_event(start_time)

    @staticmethod
    def __handle_breach_event(start_time: datetime):
        # 如果还没有创建报告，则创建报告
        if EEXIBreach.report_id is None:
            gdata.configPropperCurve.eexi_breach = True

            event_log: EventLog = EventLog.create(started_at=start_time, started_position=gdata.configGps.location)

            report_info = ReportInfo.create(event_log=event_log, report_name=f"Compliance Report #{event_log.id}")

            EEXIBreach.report_id = report_info.id
            # 记录之前所有的过载数据
            data: list[DataLog] = DataLog.select(
                DataLog.name,
                DataLog.utc_date_time,
                DataLog.speed,
                DataLog.ad_0_torque,
                DataLog.power
            ).where(
                DataLog.utc_date_time >= start_time
            ).order_by(DataLog.utc_date_time.asc())
            for item in data:
                EEXIBreach.__save_report_detail(item.name, item.utc_date_time, item.speed, item.ad_0_torque, item.power)

    @staticmethod
    def __handle_recovery_event(start_time: datetime):
        if EEXIBreach.report_id is not None:
            gdata.configPropperCurve.eexi_breach = False
            event_log: EventLog = EventLog.select().where(EventLog.ended_at == None).order_by(EventLog.id.asc()).first()

            if event_log is not None:
                event_log.ended_at = gdata.configDateTime.utc
                event_log.ended_position = gdata.configGps.location
                event_log.save()

            EEXIBreach.report_id = None
            # 记录之前所有的恢复数据
            data: list[DataLog] = DataLog.select(
                DataLog.name, DataLog.utc_date_time, DataLog.speed, DataLog.ad_0_torque, DataLog.power
            ).where(
                DataLog.utc_date_time >= start_time
            ).order_by(DataLog.utc_date_time.asc())
            for item in data:
                EEXIBreach.__save_report_detail(item.name, item.utc_date_time, item.speed, item.ad_0_torque, item.power)

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
        except:
            logging.exception("save eexi breach report detail error")
