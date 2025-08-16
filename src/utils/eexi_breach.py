import logging
from common.global_data import gdata
from db.models.event_log import EventLog
from db.models.report_detail import ReportDetail
from db.models.report_info import ReportInfo
from db.base import db


class EEXIBreach:
    report: ReportInfo | None = None
    event: EventLog | None = None
    # 大于功率列表
    over_limit_power: list[int] = []
    # 小于等于功率列表
    under_limit_power: list[int] = []

    @staticmethod
    def handle():
        # 没有开启shapoli直接关闭
        if not gdata.configCommon.shapoli:
            return

        try:
            EEXIBreach.is_breached()
            EEXIBreach.is_recovery()

            # 如果正在突破
            if gdata.configCommon.is_eexi_breaching:
                # 处理报告
                EEXIBreach.create_report_event()
                # 保存报告明细
                EEXIBreach.save_report_detail()
            else:
                EEXIBreach.update_recovery_event()
        except Exception as e:
            logging.exception(f'eexi breach判定异常:{e}')

    @staticmethod
    def is_breached():
        # 连续突破或恢复的检测时间s
        duration = gdata.configCommon.eexi_breach_checking_duration
        sum_power = EEXIBreach.get_sum_power()
        # 如果合计功率大于eexi limited power
        if sum_power > gdata.configCommon.eexi_limited_power:
            EEXIBreach.over_limit_power.append(sum_power)
            # 累计超过的功率，采集是2s一次 * 2
            over_limit_seconds = len(EEXIBreach.over_limit_power) * 2
            if over_limit_seconds > duration:
                # 大于就是突破
                gdata.configCommon.is_eexi_breaching = True
                EEXIBreach.over_limit_power.clear()
        else:
            EEXIBreach.over_limit_power.clear()

    @staticmethod
    def is_recovery():
        # 连续恢复的检测时间s
        duration = gdata.configCommon.eexi_breach_checking_duration
        sum_power = EEXIBreach.get_sum_power()
        # 如果合计功率小于等于eexi limited power
        if sum_power <= gdata.configCommon.eexi_limited_power:
            EEXIBreach.under_limit_power.append(sum_power)
            # 累计超过的功率，采集是2s一次 * 2
            under_limit_seconds = len(EEXIBreach.under_limit_power) * 2
            if under_limit_seconds > duration:
                # 大于就是恢复
                gdata.configCommon.is_eexi_breaching = False
                EEXIBreach.under_limit_power.clear()
        else:
            EEXIBreach.under_limit_power.clear()

    @staticmethod
    def get_sum_power():
        """合计功率"""
        sum_power = gdata.configSPS.power
        if gdata.configCommon.is_twins:
            sum_power += gdata.configSPS2.power
        return sum_power

    @staticmethod
    def load_exist_report_event():
        """软件启动的时候调用一下，判断是否有未完结的报告"""
        event = EventLog.get_or_none(EventLog.ended_at.is_null())
        if not event:
            return

        report = ReportInfo.get_or_none(ReportInfo.event_log == event)
        if not report:
            return

        EEXIBreach.event = event
        EEXIBreach.report = report

    @staticmethod
    def create_report_event():
        # 如果当前已经有报告和事件，跳过
        if EEXIBreach.report or EEXIBreach.event:
            return

        with db.atomic():
            # 创建事件
            EEXIBreach.event = EventLog.create(started_at=gdata.configDateTime.utc, started_position=gdata.configGps.location)
            # 创建报告
            EEXIBreach.report = ReportInfo.create(event_log=EEXIBreach.event, report_name=f"Compliance Report #{EEXIBreach.event.id}")

    @staticmethod
    def save_report_detail():
        # 15s保存一次,不然日志太多
        second = gdata.configDateTime.utc.second
        # SPS是2s采集一次，所以当前肯定是奇数或偶数
        if second not in (0, 1, 15, 16, 30, 31, 45, 46):
            return

        if not EEXIBreach.report:
            return

        with db.atomic():
            ReportDetail.create(
                report_info=EEXIBreach.report,
                name='sps', utc_date_time=gdata.configDateTime.utc,
                speed=gdata.configSPS.speed,
                torque=gdata.configSPS.torque,
                power=gdata.configSPS.power
            )

            if not gdata.configCommon.is_twins:
                return

            ReportDetail.create(
                report_info=EEXIBreach.report,
                name='sps2', utc_date_time=gdata.configDateTime.utc,
                speed=gdata.configSPS2.speed,
                torque=gdata.configSPS2.torque,
                power=gdata.configSPS2.power
            )

    @staticmethod
    def update_recovery_event():
        if EEXIBreach.event:
            EEXIBreach.event.ended_at = gdata.configDateTime.utc
            EEXIBreach.event.ended_position = gdata.configGps.location
            EEXIBreach.event.save()

        EEXIBreach.report = None
        EEXIBreach.event = None
