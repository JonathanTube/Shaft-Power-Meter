import flet as ft

from ui.setting.logs.breach_logger import BreachLogger
from ui.setting.logs.data_logger import DataLogger
from ui.setting.logs.gps_logger import GpsLogger


class Logs(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__create()

    def __create(self):
        return ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Breach Log", content=BreachLogger()),
                ft.Tab(text="Data Log", content=DataLogger()),
                ft.Tab(text="GPS Log", content=GpsLogger())
            ],
            expand=True
        )
