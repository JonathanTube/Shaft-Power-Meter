import datetime
import flet as ft

from ui.common.datetime_search import DatetimeSearch
from ui.report.report_info_table import ReportInfoTable

class ReportInfoList(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

    def build(self):
        search = DatetimeSearch(self.__on_search)
        self.table = ReportInfoTable()

        self.content = ft.Column(
            expand=True,
            controls=[
                search,
                self.table
            ]
        )

    def __on_search(self, start_date: str, end_date: str):
        self.table.search(start_date=start_date, end_date=end_date)
