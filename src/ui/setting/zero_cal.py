import flet as ft

from src.ui.setting.zero_cal_executor import ZeroCalExecutor
from src.ui.setting.zero_cal_his import ZeroCalHis


class ZeroCal:
    @staticmethod
    def create():
        return ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Zero Cal.",
                    icon=ft.Icons.ADJUST_OUTLINED,
                    content=ft.Container(
                        padding=ft.padding.symmetric(10, 20),
                        content=ZeroCalExecutor().create()
                    )
                ),

                ft.Tab(
                    text="Zero Cal. History",
                    icon=ft.icons.HISTORY_OUTLINED,
                    content=ft.Container(
                        padding=ft.padding.symmetric(10, 20),
                        content=ZeroCalHis().create()
                    )
                )

            ],
            expand=True
        )
