import flet as ft
from datetime import datetime
from db.models.data_log import DataLog
from ui.common.datetime_search import DatetimeSearch
from ui.home.trendview.diagram import TrendViewDiagram
from ui.common.toast import Toast
from db.models.system_settings import SystemSettings
from db.models.date_time_conf import DateTimeConf
import logging
from typing import Literal
from peewee import fn


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
        try:
            self.search = DatetimeSearch(self.__on_search)
            self.sps_chart = TrendViewDiagram()

            if self.is_twins:
                self.sps2_chart = TrendViewDiagram()
                self.content = ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        self.search,
                        ft.Tabs(
                            expand=True,
                            tabs=[
                                ft.Tab(text='SPS', content=self.sps_chart),
                                ft.Tab(text='SPS2', content=self.sps2_chart)
                            ]
                        )
                    ]
                )
            else:
                self.content = ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[self.search, self.sps_chart]
                )
        except:
            logging.exception('exception occured at TrendView.build')

    def __on_search(self, start_date: str, end_date: str):
        if not start_date or not end_date:
            return
        try:
            if self.page and self.page.session:
                date_time_format = f"{self.date_format} %H:%M:%S"
                days_diff = (datetime.strptime(end_date, date_time_format) - datetime.strptime(start_date, date_time_format)).days
                if days_diff > 90:
                    Toast.show_error(self.page, self.page.session.get('lang.trendview.cannot_search_more_than_90_days'))
                    return
                self.handle_data(start_date, end_date, 'sps')
                if self.is_twins:
                    self.handle_data(start_date, end_date, 'sps2')
        except:
            pass

    def handle_data(self, start_date: str, end_date: str, name: Literal['sps', 'sps2']):
        cnt = (
            DataLog.select(fn.COUNT(DataLog.id))
            .where(
                (DataLog.utc_date_time >= start_date) &
                (DataLog.utc_date_time <= end_date) &
                (DataLog.name == name)
            ).scalar() or 0
        )
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
        if name == 'sps':
            self.sps_chart.update_chart(data_logs)
        elif name == 'sps2':
            self.sps2_chart.update_chart(data_logs)
