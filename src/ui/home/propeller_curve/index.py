import flet as ft

from common.control_manager import ControlManager
from ui.home.propeller_curve.diagram import PropellerCurveDiagram


class PropellerCurve(ft.Container):
    def __init__(self):
        super().__init__()

    def build(self):
        self.diagram = PropellerCurveDiagram()
        ControlManager.propeller_curve_diagram = self.diagram
        self.content = self.diagram

    def will_unmount(self):
        ControlManager.propeller_curve_diagram = None
