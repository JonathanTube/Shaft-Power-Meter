from typing import Callable
import flet as ft
from ui.common.date_time_range import DateTimeRange


class DatetimeSearch(ft.Card):
    def __init__(self, on_search: Callable[[str, str], None]):
        super().__init__()
        self.margin = 0
        self.on_search = on_search


    def build(self):
        self.date_time_range = DateTimeRange()

        self.search_button = ft.OutlinedButton(
            icon=ft.Icons.SEARCH_OUTLINED,
            text="Search",
            on_click=self.__handle_search
        )

        search_row = ft.Row(controls=[
            self.date_time_range,
            self.search_button
        ])
        self.content = ft.Container(content=search_row, padding=10)

    def __handle_search(self, e):
        start_date, end_date = self.date_time_range.get_date_range()
        if start_date == "" or end_date == "":
            return
        if start_date:
            start_date = f"{start_date} 00:00:00"
        if end_date:
            end_date = f"{end_date} 23:59:59"
        self.on_search(start_date, end_date)
