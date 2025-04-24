import flet as ft

from ui.common.datetime_search import DatetimeSearch
from ui.home.event.event_table import EventTable


class EventList(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10
        self.content = self.__create()

    def __create(self):
        search = DatetimeSearch(self.on_search)
        self.table = EventTable()

        return ft.Column(
            expand=True,
            spacing=5,
            controls=[
                search,
                self.table
            ]
        )

    def on_search(self, start_date: str, end_date: str):
        self.table.search(start_date=start_date, end_date=end_date)
