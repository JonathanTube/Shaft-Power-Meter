import asyncio
import logging
from common.global_data import gdata
from db.models.event_log import EventLog
from db.models.report_detail import ReportDetail
from db.models.report_info import ReportInfo
from db.base import db
from peewee import fn


class EEXIBreachTask:
    def __init__(self):
        self.report: ReportInfo | None = None
        self.event: EventLog | None = None
        # 大于功率列表
        self.over_limit_power: list[int] = []
        # 小于等于功率列表
        self.under_limit_power: list[int] = []
        # 控制循环的标志
        self.running = False
        # asyncio任务引用
        self._task: asyncio.Task | None = None

    async def start(self):
        """启动后台循环（非阻塞）"""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run_loop())

    async def _run_loop(self):
        """每秒执行一次 handle 的异步循环"""
        self.running = True
        self.load_exist_report_event()
        while self.running and gdata.configCommon.shapoli:
            self.handle()
            await asyncio.sleep(1)

    def stop(self):
        """停止循环"""
        self.running = False
        if self._task and not self._task.done():
            self._task.cancel()

    def handle(self):
        try:
            self.is_breached()
            self.is_recovery()

            # 如果正在突破
            if gdata.configCommon.is_eexi_breaching:
                # 处理报告
                self.create_report_event()
                # 保存报告明细
                self.save_report_detail()
            else:
                self.update_recovery_event()
        except Exception as e:
            logging.exception(f'eexi breach判定异常:{e}')

    def is_breached(self):
        # 连续突破或恢复的检测时间s
        duration = gdata.configCommon.eexi_breach_checking_duration
        sum_power = self.get_sum_power()
        # 如果合计功率大于eexi limited power
        if sum_power > gdata.configCommon.eexi_limited_power:
            self.over_limit_power.append(sum_power)
            # 累计超过的功率，采集是1s一次
            over_limit_seconds = len(self.over_limit_power)
            if over_limit_seconds > duration:
                # 大于就是突破
                gdata.configCommon.is_eexi_breaching = True
                self.over_limit_power.clear()
        else:
            self.over_limit_power.clear()

    def is_recovery(self):
        # 连续恢复的检测时间s
        duration = gdata.configCommon.eexi_breach_checking_duration
        sum_power = self.get_sum_power()
        # 如果合计功率小于等于eexi limited power
        if sum_power <= gdata.configCommon.eexi_limited_power:
            self.under_limit_power.append(sum_power)
            # 累计超过的功率，采集是1s一次
            under_limit_seconds = len(self.under_limit_power)
            if under_limit_seconds > duration:
                # 大于就是恢复
                gdata.configCommon.is_eexi_breaching = False
                self.under_limit_power.clear()
        else:
            self.under_limit_power.clear()

    def get_sum_power(self):
        """合计功率"""
        # 如果测试模式打开，直接取测试模式的数值就行了
        if gdata.configTest.test_mode_running:
            sum_power = gdata.configSPS.power
            if gdata.configCommon.is_twins:
                sum_power += gdata.configSPS2.power
            return sum_power

        sum_power = gdata.configSPS.power_for_1s
        if gdata.configCommon.is_twins:
            sum_power += gdata.configSPS2.power_for_1s
        return sum_power

    def load_exist_report_event(self):
        """软件启动的时候调用一下，判断是否有未完结的报告"""
        event = EventLog.get_or_none(EventLog.ended_at.is_null())
        if not event:
            return

        report = ReportInfo.get_or_none(ReportInfo.event_log == event)
        if not report:
            return

        self.event = event
        self.report = report

    def create_report_event(self):
        # 如果当前已经有报告和事件，跳过
        if self.report or self.event:
            return

        with db.atomic():
            # 创建事件
            self.event = EventLog.create(started_at=gdata.configDateTime.utc, started_position=gdata.configGps.location)
            # 创建报告
            self.report = ReportInfo.create(event_log=self.event, report_name=f"Compliance Report #{self.event.id}")

        cnt = EventLog.select(fn.COUNT(EventLog.id)).where(EventLog.breach_reason.is_null()).scalar()
        gdata.configEvent.not_confirmed_count = cnt

    def save_report_detail(self):
        # 15s保存一次,不然日志太多
        second = gdata.configDateTime.utc.second
        if second not in (0, 15, 30, 45):
            return

        if not self.report:
            return

        with db.atomic():
            if gdata.configTest.test_mode_running:
                ReportDetail.create(
                    report_info=self.report,
                    name='sps', utc_date_time=gdata.configDateTime.utc,
                    speed=gdata.configSPS.speed,
                    torque=gdata.configSPS.torque,
                    power=gdata.configSPS.power
                )
            else:
                ReportDetail.create(
                    report_info=self.report,
                    name='sps', utc_date_time=gdata.configDateTime.utc,
                    speed=gdata.configSPS.speed_for_15s,
                    torque=gdata.configSPS.torque_for_15s,
                    power=gdata.configSPS.power_for_15s
                )

            if not gdata.configCommon.is_twins:
                return

            if gdata.configTest.test_mode_running:
                ReportDetail.create(
                    report_info=self.report,
                    name='sps2', utc_date_time=gdata.configDateTime.utc,
                    speed=gdata.configSPS2.speed,
                    torque=gdata.configSPS2.torque,
                    power=gdata.configSPS2.power
                )
            else:
                ReportDetail.create(
                    report_info=self.report,
                    name='sps2', utc_date_time=gdata.configDateTime.utc,
                    speed=gdata.configSPS2.speed_for_15s,
                    torque=gdata.configSPS2.torque_for_15s,
                    power=gdata.configSPS2.power_for_15s
                )

    def update_recovery_event(self):
        if self.event:
            self.event.ended_at = gdata.configDateTime.utc
            self.event.ended_position = gdata.configGps.location
            self.event.save()

        self.report = None
        self.event = None


# 初始化实例
eexi_breach_task: EEXIBreachTask = EEXIBreachTask()
