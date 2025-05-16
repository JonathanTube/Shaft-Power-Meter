import flet as ft

from ui.setting.zero_cal.zero_cal_executor import ZeroCalExecutor
from ui.setting.zero_cal.zero_cal_his import ZeroCalHis


class ZeroCal(ft.Container):
    def __init__(self):
        super().__init__()

    def build(self):
        self.content = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text=self.page.session.get("lang.zero_cal.executor"),
                    content=ft.Container(
                        padding=ft.padding.only(top=10, bottom=5),
                        content=ZeroCalExecutor()
                    )
                ),

                ft.Tab(
                    text=self.page.session.get("lang.zero_cal.history"),
                    content=ft.Container(
                        padding=ft.padding.symmetric(0, 0),
                        content=ZeroCalHis()
                    )
                )

            ],
            expand=True
        )
