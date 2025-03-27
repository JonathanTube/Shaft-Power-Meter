import flet as ft

from ui.home.propeller_curve.propeller_curve_chart import PropellerCurveChart
from ui.home.propeller_curve.propeller_curve_legend import PropellerCurveLegend


class PropellerCurve(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 20

    def build(self):
        self.chart = PropellerCurveChart()
        self.legend = PropellerCurveLegend()
        self.content = ft.Stack(
            alignment=ft.alignment.center,
            controls=[
                self.legend,
                self.chart
            ])

    def did_mount(self):
        self.chart.set_normal_propeller_curve(
            79.5, 50, 100, 100, 0.05, 105, 0.05)
