import flet as ft

from ui.home.logs.log_data.log_data_list import LogDataList
from ui.home.logs.log_gps.log_gps_list import LogGpsList


class Logs(ft.Container):
    def build(self):
        self.content = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Data Log", content=LogDataList()),
                ft.Tab(text="GPS Log", content=LogGpsList())
            ],
            expand=True
        )

    def set_language(self):
        session = self.page.session
        self.content.tabs[0].text = session.get("lang.log.data_log")
        self.content.tabs[1].text = session.get("lang.log.gps_log")

    def before_update(self):
        self.set_language()

    def did_mount(self):
        self.set_language()
