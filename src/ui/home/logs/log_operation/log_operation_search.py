import logging
import flet as ft
from typing import Callable
from ui.common.date_time_range import DateTimeRange
from common.operation_type import OperationType


class LogOperationSearch(ft.Container):
    def __init__(self, on_search: Callable[[str, str, int], None]):
        super().__init__()
        self.on_search = on_search

    def build(self):
        try:
            self.date_time_range = DateTimeRange()

            self.search_button = ft.OutlinedButton(
                icon=ft.Icons.SEARCH_OUTLINED,
                height=45,
                text=self.page.session.get("lang.button.search"),
                on_click=self.__handle_search
            )

            self.operation_type = ft.Dropdown(
                label=self.page.session.get("lang.operation_log.operation_type"),
                options=[ft.dropdown.Option(text=OperationType.get_operation_type_name(item.value), key=item.value) for item in OperationType]
            )

            self.content = ft.Row(controls=[self.date_time_range, self.operation_type, self.search_button])
        except:
            logging.exception('exception occured at LogOperationSearch.build')

    def __handle_search(self, e):
        start_date, end_date = self.date_time_range.get_date_range()
        operation_type = self.operation_type.value

        _start_date = None
        _end_date = None
        if start_date != "" and end_date != "":
            start_date = f"{start_date} 00:00:00"
            end_date = f"{end_date} 23:59:59"

        self.on_search(_start_date, _end_date, operation_type)
