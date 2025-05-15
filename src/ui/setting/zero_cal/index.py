import flet as ft

from ui.setting.zero_cal.zero_cal_executor import ZeroCalExecutor
from ui.setting.zero_cal.zero_cal_his import ZeroCalHis


class ZeroCal:
    @staticmethod
    def create():
        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Zero Cal.",
                    content=ft.Container(
                        padding=ft.padding.symmetric(10, 0),
                        content=ZeroCalExecutor()
                    )
                ),

                ft.Tab(
                    text="Zero Cal. History",
                    content=ft.Container(
                        padding=ft.padding.symmetric(0, 0),
                        content=ZeroCalHis()
                    )
                )

            ],
            expand=True
        )
