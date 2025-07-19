import logging
from typing import Callable
import flet as ft
from ui.common.date_time_range import DateTimeRange


class DatetimeSearch(ft.Container):
    def __init__(self, on_search: Callable[[str, str], None]):
        super().__init__()
        self.on_search = on_search

    def build(self):
        try:
            if self.page and self.page.session:
                self.date_time_range = DateTimeRange()

                self.search_button = ft.OutlinedButton(
                    icon=ft.Icons.SEARCH_OUTLINED,
                    height=40,
                    text=self.page.session.get("lang.button.search"),
                    on_click=self.__handle_search
                )

                self.content = ft.Row(controls=[
                    self.date_time_range,
                    self.search_button
                ])
        except:
            logging.exception('exception occured at DatetimeSearch.build')


    def __handle_search(self, e):
        try:
            if self.page and self.date_time_range:
                start_date, end_date = self.date_time_range.get_date_range()

                if start_date == "" or end_date == "":
                    if self.on_search is not None:
                        self.on_search(None, None)
                    return

                if start_date is not None:
                    start_date = f"{start_date} 00:00:00"

                if end_date is not None:
                    end_date = f"{end_date} 23:59:59"

                if self.on_search is not None:
                    self.on_search(start_date, end_date)
        except:
            logging.exception('exception occured at DatetimeSearch.__handle_search')