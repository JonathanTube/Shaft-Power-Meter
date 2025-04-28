import flet as ft
from datetime import datetime
from db.models.data_log import DataLog
from ui.common.datetime_search import DatetimeSearch
from ui.home.trendview.diagram import TrendViewDiagram
from common.control_manager import ControlManager
from ui.common.toast import Toast
from db.models.date_time_conf import DateTimeConf


class TrendView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        # self.bgcolor = ft.colors.BLUE
        self.padding = 10
        datetime_conf: DateTimeConf = DateTimeConf.get()
        self.date_format = datetime_conf.date_format

    def build(self):
        search = DatetimeSearch(self.__on_search)
        self.trend_view_chart = TrendViewDiagram()
        ControlManager.trend_view_diagram = self.trend_view_chart
        self.content = ft.Column(
            expand=True,
            controls=[search, self.trend_view_chart]
        )

    def __on_search(self, start_date: str, end_date: str):
        if not start_date or not end_date:
            return

        date_time_format = f"{self.date_format} %H:%M:%S"
        days_diff = (datetime.strptime(end_date, date_time_format) - datetime.strptime(start_date, date_time_format)).days
        if days_diff > 15:
            Toast.show_error(self.page, self.page.session.get('lang.trendview.cannot_search_more_than_15_days'))
            return

        data_logs = DataLog.select(
            DataLog.power,
            DataLog.speed,
            DataLog.utc_date_time
        ).where(
            DataLog.name == "sps1"
        ).where(
            DataLog.utc_date_time >= start_date,
            DataLog.utc_date_time <= end_date
        ).order_by(DataLog.id.desc())

        self.trend_view_chart.update_chart(data_logs)

    def will_unmount(self):
        ControlManager.trend_view_diagram = None
