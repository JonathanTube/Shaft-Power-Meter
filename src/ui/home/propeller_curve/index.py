import flet as ft

from ui.home.propeller_curve.diagram import PropellerCurveDiagram


class PropellerCurve(ft.Container):
    def build(self):
        self.content = PropellerCurveDiagram()
