import flet as ft
from datetime import datetime
from db.models.system_settings import SystemSettings
from ui.common.datetime_search import DatetimeSearch
from ui.home.trendview.trendview_chart import TrendviewChart
from ui.common.toast import Toast


class TrendView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

        system_settings: SystemSettings = SystemSettings.get()
        self.amount_of_propeller = system_settings.amount_of_propeller

    def build(self):
        search = DatetimeSearch(self.__on_search)
        self.chart_sps1 = TrendviewChart("sps1")

        self.content = ft.Column(
            expand=True,
            spacing=10,
            controls=[search, self.chart_sps1]
        )
        if self.amount_of_propeller == 2:
            self.chart_sps2 = TrendviewChart("sps2")
            self.content.controls.append(self.chart_sps2)

    def __on_search(self, start_date: str, end_date: str):
        if not start_date or not end_date:
            return

        days_diff = (datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S") - datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")).days
        if days_diff > 30:
            Toast.show_error(self.page, self.page.session.get('lang.trendview.cannot_search_more_than_30_days'))
            return

        self.chart_sps1.reload(start_date, end_date)
        if self.amount_of_propeller == 2:
            self.chart_sps2.reload(start_date, end_date)
