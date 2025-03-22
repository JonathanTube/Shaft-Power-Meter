import flet as ft

from ui.home.dashboard.single.on.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.single.on.instant_value_grid import InstantValueGrid


class SingleShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()

    def __create_left(self):
        w = self.page.window.width
        h = self.page.window.height
        return EEXILimitedPower(w * 0.46, h * 0.4)

    def __create_right(self):
        w = self.page.window.width
        h = self.page.window.height
        return InstantValueGrid(w * 0.46, h * 0.4)

    def build(self):
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[self.__create_left(), self.__create_right()]
        )
