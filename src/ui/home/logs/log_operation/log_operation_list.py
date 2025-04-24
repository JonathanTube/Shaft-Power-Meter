import flet as ft

from ui.common.datetime_search import DatetimeSearch
from ui.home.logs.log_operation.log_operation_table import LogOperationTable


class LogOperationList(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

    def build(self):
        search = DatetimeSearch(self.__on_search)
        self.table = LogOperationTable()

        self.content = ft.Column(
            expand=True,
            spacing=5,
            controls=[search, self.table]
        )

    def __on_search(self, start_date: str, end_date: str):
        self.table.search(start_date=start_date, end_date=end_date)
