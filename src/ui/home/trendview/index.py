import flet as ft

from db.models.data_log import DataLog
from ui.common.datetime_search import DatetimeSearch
from ui.home.trendview.trendview_chart import TrendViewChart


class TrendView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        # self.bgcolor = ft.colors.BLUE
        self.padding = 10

    def build(self):
        search = DatetimeSearch(self.__on_search)
        self.trend_view_chart = TrendViewChart()
        self.content = ft.Column(
            expand=True,
            controls=[
                search,
                self.trend_view_chart
            ]
        )

    def __on_search(self, start_date: str, end_date: str):
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
