import flet as ft

from ui.home.dashboard.sps_dual.on.dual_instant_grid import DualInstantGrid
from ui.home.dashboard.eexi.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.chart.single_power_line import SinglePowerLine


class DualShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()

    def build(self):
        w = self.page.window.width * 0.5
        h = self.page.window.height * 0.5

        self.eexi_limited_power = EEXILimitedPower(w, h)
        self.instant_grid = DualInstantGrid()
        self.power_chart = SinglePowerLine()

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Row(expand=True, controls=[self.eexi_limited_power, self.instant_grid]),
                ft.Row(expand=True, controls=[self.power_chart])
            ]
        )

    def did_mount(self):
        self.load_data()

    def load_data(self):
        self.instant_grid.reload()
        self.eexi_limited_power.reload()
        self.power_chart.reload()
