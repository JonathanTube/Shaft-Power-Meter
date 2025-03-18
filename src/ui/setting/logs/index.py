import flet as ft

from ui.setting.logs.breach import BreachLog
from ui.setting.logs.data import DataLog
from ui.setting.logs.gps import GpsLog


class Logs(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__create()

    def __create(self):
        return ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Breach Log", content=BreachLog()),
                ft.Tab(text="Data Log", content=DataLog()),
                ft.Tab(text="GPS Log", content=GpsLog())
            ],
            expand=True
        )
