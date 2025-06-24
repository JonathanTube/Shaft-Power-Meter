import logging
import flet as ft

from ui.home.propeller_curve.diagram import PropellerCurveDiagram


class PropellerCurve(ft.Container):
    def build(self):
        try:
            self.content = PropellerCurveDiagram()
        except:
            logging.exception('exception occured at PropellerCurve.build')


