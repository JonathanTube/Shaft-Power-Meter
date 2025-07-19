import logging
import flet as ft

from ui.home.dashboard.sps_dual.off.index import DualShaPoLiOff
from ui.home.dashboard.sps_dual.on.index import DualShaPoLiOn
from ui.home.dashboard.sps_single.off.index import SingleShaPoLiOff
from ui.home.dashboard.sps_single.on.index import SingleShaPoLiOn
from db.models.system_settings import SystemSettings


class Dashboard(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 10
        self.system_settings: SystemSettings = SystemSettings.get()

    def build(self):
        try:
            sha_po_li = self.system_settings.sha_po_li
            amount_of_power = self.system_settings.amount_of_propeller

            if amount_of_power == 1:
                if sha_po_li:
                    self.content = SingleShaPoLiOn()
                else:
                    self.content = SingleShaPoLiOff()
            elif amount_of_power == 2:
                if sha_po_li:
                    self.content = DualShaPoLiOn()
                else:
                    self.content = DualShaPoLiOff()
        except:
            logging.exception('exception occured at Dashboard.build')
