import logging
import flet as ft

from db.models.system_settings import SystemSettings
from ui.home.logs.log_data.log_data_list import LogDataList
from ui.home.logs.log_gps.log_gps_list import LogGpsList
from ui.home.logs.log_operation.log_operation import LogOperation


class Logs(ft.Container):
    def __init__(self):
        super().__init__()
        self.system_settings: SystemSettings = SystemSettings.get()

    def build(self):
        try:
            tabs = [
                ft.Tab(text=self.page.session.get("lang.log.data_log"), content=LogDataList()),
                ft.Tab(text=self.page.session.get("lang.log.operation_log"), content=LogOperation())
            ]

            if self.system_settings.enable_gps:
                tabs.insert(1, ft.Tab(text=self.page.session.get("lang.log.gps_log"), content=LogGpsList()))

            self.content = ft.Tabs(
                selected_index=0,
                tabs=tabs,
                expand=True
            )
        except:
            logging.exception('exception occured at Logs.build')
