import flet as ft

from ui.home.dashboard.single.power_chart import PowerChart
from ui.home.dashboard.single.on.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.single.on.instant_value_grid import InstantValueGrid


class SingleShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()

    def __create_top_left(self):
        w = self.page.window.width
        h = self.page.window.height
        return EEXILimitedPower(w * 0.46, h * 0.4)

    def __create_top_right(self):
        w = self.page.window.width
        h = self.page.window.height
        return InstantValueGrid(w * 0.46, h * 0.4)

    def __create_top(self):
        self.top = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[self.__create_top_left(), self.__create_top_right()]
        )

    def __create_bottom(self):
        self.bottom = ft.Container(
            content=PowerChart(),
            expand=True
        )

    def build(self):
        self.__create_top()
        self.__create_bottom()

        self.content = ft.Column(
            controls=[self.top, self.bottom],
            expand=True
        )
