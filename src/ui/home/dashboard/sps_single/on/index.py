import flet as ft

from ui.home.dashboard.chart.single_power_line import SinglePowerLine
from ui.home.dashboard.eexi.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.sps_single.on.single_instant_grid import SingleInstantGrid


class SingleShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()

    def build(self):
        w = self.page.window.width * 0.5
        h = self.page.window.height * 0.5

        self.eexi_limited_power = EEXILimitedPower(w, h)
        self.instant_value_grid = SingleInstantGrid(w, h)
        self.power_line_chart = SinglePowerLine()

        self.content = ft.Column(
            controls=[
                ft.Row(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[self.eexi_limited_power, self.instant_value_grid]
                ),
                self.power_line_chart
            ],
            expand=True
        )

    def did_mount(self):
        self.load_data()

    def load_data(self):
        self.eexi_limited_power.reload()
        self.instant_value_grid.reload()
        self.power_line_chart.reload()
