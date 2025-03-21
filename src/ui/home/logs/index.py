import flet as ft

from ui.home.logs.log_data.log_data_list import LogDataList
from ui.home.logs.log_gps.log_gps_list import LogGpsList
from ui.home.logs.logs_event.log_event_list import LogEventList


class Logs(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__create()

    def __create(self):
        return ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Breach Log", content=LogEventList()),
                ft.Tab(text="Data Log", content=LogDataList()),
                ft.Tab(text="GPS Log", content=LogGpsList())
            ],
            expand=True
        )
