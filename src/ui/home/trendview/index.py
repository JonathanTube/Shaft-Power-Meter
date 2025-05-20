import flet as ft
from datetime import datetime
from db.models.data_log import DataLog
from ui.common.datetime_search import DatetimeSearch
from ui.home.trendview.diagram import TrendViewDiagram
from common.control_manager import ControlManager
from ui.common.toast import Toast
from db.models.system_settings import SystemSettings
from db.models.date_time_conf import DateTimeConf
import logging
from typing import Literal


class TrendView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

        system_settings: SystemSettings = SystemSettings.get()
        self.is_twins = system_settings.amount_of_propeller == 2
        datetime_conf: DateTimeConf = DateTimeConf.get()
        self.date_format = datetime_conf.date_format

    def build(self):
        self.search = DatetimeSearch(self.__on_search)
        self.sps1_chart = TrendViewDiagram()
        ControlManager.trend_view_sps1 = self.sps1_chart

        if self.is_twins:
            self.sps2_chart = TrendViewDiagram()
            ControlManager.trend_view_sps2 = self.sps2_chart
            self.content = ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    self.search,
                    ft.Tabs(
                        expand=True,
                        tabs=[
                            ft.Tab(text='SPS1', content=self.sps1_chart),
                            ft.Tab(text='SPS2', content=self.sps2_chart)
                        ]
                    )
                ]
            )
        else:
            self.content = ft.Column(
                expand=True,
                spacing=0,
                controls=[self.search, self.sps1_chart]
            )

    def __on_search(self, start_date: str, end_date: str):
        if not start_date or not end_date:
            return

        date_time_format = f"{self.date_format} %H:%M:%S"
        days_diff = (datetime.strptime(end_date, date_time_format) - datetime.strptime(start_date, date_time_format)).days
        if days_diff > 90:
            Toast.show_error(self.page, self.page.session.get('lang.trendview.cannot_search_more_than_90_days'))
            return
        self.handle_data(start_date, end_date, 'sps1')
        if self.is_twins:
            self.handle_data(start_date, end_date, 'sps2')
        self.page.session.set('trendview_start_date', start_date)
        self.page.session.set('trendview_end_date', end_date)

    def handle_data(self, start_date: str, end_date: str, name: Literal['sps1', 'sps2']):
        cnt = DataLog.select().where(DataLog.utc_date_time >= start_date, DataLog.utc_date_time <= end_date).where(DataLog.name == name).count()
        logging.info(f"trendview query data count: {cnt}")
        max_data_count = 8000
        # 假设chart最优显示8000条数据,那么需要分段查询
        portion = (cnt + max_data_count) // max_data_count
        logging.info(f"{name} trendview query data portion: {portion}")
        data_logs = DataLog.select(
            DataLog.power,
            DataLog.speed,
            DataLog.utc_date_time
        ).where(
            DataLog.utc_date_time >= start_date,
            DataLog.utc_date_time <= end_date
        ).where(DataLog.name == name).where(DataLog.id % portion == 0).order_by(DataLog.id.desc())
        if name == 'sps1':
            self.sps1_chart.update_chart(data_logs)
        elif name == 'sps2':
            self.sps2_chart.update_chart(data_logs)

    def will_unmount(self):
        ControlManager.trend_view_sps1 = None
        ControlManager.trend_view_sps2 = None

    def did_mount(self):
        start_date: str = self.page.session.get('trendview_start_date')
        end_date: str = self.page.session.get('trendview_end_date')
        if start_date and end_date:
            self.__on_search(start_date, end_date)

            start_date = start_date.split(' ')[0]
            end_date = end_date.split(' ')[0]
            print(f"start_date: {start_date}, end_date: {end_date}")
            self.search.date_time_range.start_date.value = start_date
            self.search.date_time_range.end_date.value = end_date
            self.search.update()
