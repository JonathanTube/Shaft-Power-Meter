import flet as ft
from datetime import datetime
from db.models.data_log import DataLog
from ui.common.datetime_search import DatetimeSearch
from ui.home.trendview.trendview_chart import TrendViewChart
from ui.common.toast import Toast


class TrendView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        # self.bgcolor = ft.Colors.BLUE
        self.padding = 10

    def build(self):
        search = DatetimeSearch(self.__on_search)
        self.trend_view_chart = TrendViewChart()
        self.content = ft.Column(
            expand=True,
            controls=[search,self.trend_view_chart]
        )

    def __on_search(self, start_date: str, end_date: str):
        if not start_date or not end_date:
            return

        days_diff = (datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S") - datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")).days
        if days_diff > 30:
            Toast.show_error(self.page, self.page.session.get('lang.trendview.cannot_search_more_than_30_days'))
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
