import logging
import flet as ft

from ui.home.dashboard.sps_dual.off.index import DualShaPoLiOff
from ui.home.dashboard.sps_dual.on.index import DualShaPoLiOn
from ui.home.dashboard.sps_single.off.index import SingleShaPoLiOff
from ui.home.dashboard.sps_single.on.index import SingleShaPoLiOn
from common.global_data import gdata


class Dashboard(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 10

    def build(self):
        try:
            if gdata.configCommon.is_twins:
                if gdata.configCommon.shapoli:
                    self.content = DualShaPoLiOn()
                else:
                    self.content = DualShaPoLiOff()
                return

            if gdata.configCommon.shapoli:
                self.content = SingleShaPoLiOn()
            else:
                self.content = SingleShaPoLiOff()

        except:
            logging.exception('exception occured at Dashboard.build')
