import flet as ft

from ui.setting.zero_cal.zero_cal_executor_sps1 import ZeroCalExecutorSPS1
from ui.setting.zero_cal.zero_cal_executor_sps2 import ZeroCalExecutorSPS2
from ui.setting.zero_cal.zero_cal_his import ZeroCalHis
from db.models.system_settings import SystemSettings


class ZeroCal(ft.Container):
    def __init__(self):
        super().__init__()
        system_settings: SystemSettings = SystemSettings.get()
        self.amount_of_propeller = system_settings.amount_of_propeller

    def __on_change(self, e):
        data = int(e.data)
        if data == 0:
            self.his.table.search()

    def build(self):
        self.executor_sps1 = ft.Tab(
            text=f'{self.page.session.get("lang.zero_cal.executor")} SPS1',
            content=ft.Container(
                padding=ft.padding.only(top=10, bottom=5),
                content=ZeroCalExecutorSPS1()
            )
        )
        self.executor_sps2 = ft.Tab(
            text=f'{self.page.session.get("lang.zero_cal.executor")} SPS2',
            content=ft.Container(
                padding=ft.padding.only(top=10, bottom=5),
                content=ZeroCalExecutorSPS2()
            )
        )
        self.his = ZeroCalHis()
        tabs = [
                ft.Tab(
                    text=self.page.session.get("lang.zero_cal.history"),
                    content=ft.Container(
                        padding=ft.padding.symmetric(0, 0),
                        content=self.his
                    )
                ),
                self.executor_sps1
        ]
        if self.amount_of_propeller > 1:
            tabs.append(self.executor_sps2)

        self.content = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            on_change=lambda e: self.__on_change(e),
            tabs=tabs,
            expand=True
        )
