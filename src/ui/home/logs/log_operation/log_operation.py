import logging
import flet as ft

from ui.home.logs.log_operation.log_operation_search import LogOperationSearch
from ui.home.logs.log_operation.log_operation_table import LogOperationTable


class LogOperation(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

    def build(self):
        try:
            search = LogOperationSearch(self.__on_search)
            self.table = LogOperationTable()

            self.content = ft.Column(
                expand=True,
                spacing=5,
                controls=[search, self.table]
            )
        except:
            logging.exception('exception occured at LogOperation.build')

    def __on_search(self, start_date: str, end_date: str, operation_type: int):
        self.table.search(start_date=start_date, end_date=end_date, operation_type=operation_type)
