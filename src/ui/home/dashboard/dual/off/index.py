import flet as ft
from ui.home.dashboard.dual.off.dual_meters import DualMeters
from ui.home.dashboard.chart.dual_power_chart import DualPowerChart


class DualShaPoLiOff(ft.Container):
    def __init__(self):
        super().__init__()

    def __create_top(self):
        self.top = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            controls=[
                DualMeters(name="SPS1"),
                DualMeters(name="SPS2")
            ]
        )

    def __create_bottom(self):
        self.bottom = DualPowerChart()

    def build(self):
        self.__create_top()
        self.__create_bottom()

        self.content = ft.Column(
            expand=True,
            spacing=20,
            alignment=ft.alignment.center,
            controls=[
                self.top,
                self.bottom
            ]
        )
