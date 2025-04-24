import flet as ft

from ui.home.logs.log_data.log_data_list import LogDataList
from ui.home.logs.log_gps.log_gps_list import LogGpsList
from ui.home.logs.log_operation.log_operation_list import LogOperationList


class Logs(ft.Container):
    def build(self):
        self.content = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text=self.page.session.get("lang.log.data_log"), content=LogDataList()),
                ft.Tab(text=self.page.session.get("lang.log.gps_log"), content=LogGpsList()),
                ft.Tab(text=self.page.session.get("lang.log.operation_log"), content=LogOperationList())
            ],
            expand=True
        )
