import logging
import flet as ft

from ui.common.datetime_search import DatetimeSearch
from ui.home.logs.log_data.log_data_table import LogDataTable


class LogDataList(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

    def build(self):
        try:
            search = DatetimeSearch(self.__on_search)
            self.table = LogDataTable()

            self.content = ft.Column(
                expand=True,
                spacing=5,
                controls=[search, self.table]
            )
        except:
            logging.exception('exception occured at LogDataList.build')

    def __on_search(self, start_date: str, end_date: str):
        self.table.search(start_date=start_date, end_date=end_date)
