import logging
import flet as ft

from ui.setting.zero_cal.zero_cal_executor_sps import ZeroCalExecutorSPS
from ui.setting.zero_cal.zero_cal_executor_sps2 import ZeroCalExecutorSPS2
from ui.setting.zero_cal.zero_cal_his import ZeroCalHis
from db.models.system_settings import SystemSettings


class ZeroCal(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.alignment=ft.alignment.center
        self.system_settings: SystemSettings = SystemSettings.get()

    def __on_change(self, e):
        data = int(e.data)
        if data == 0:
            self.his.table.search()

    def build(self):
        try:
            if self.page and self.page.session:
                if not self.system_settings.is_master:
                    self.content = ft.Text(value=self.page.session.get('lang.setting.zero_cal.disabled'), size=20)
                    return


                self.executor_sps = ft.Tab(
                    text=f'{self.page.session.get("lang.zero_cal.executor")} SPS',
                    content=ft.Container(
                        padding=ft.padding.only(top=10, bottom=5),
                        content=ZeroCalExecutorSPS()
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
                    self.executor_sps
                ]

                if self.system_settings.amount_of_propeller > 1:
                    tabs.append(self.executor_sps2)

                self.content = ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    on_change=lambda e: self.__on_change(e),
                    tabs=tabs,
                    expand=True
                )
        except:
            logging.exception('exception occured at ZeroCal.build')