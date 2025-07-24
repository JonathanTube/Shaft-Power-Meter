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

        self.sha_po_li = True
        self.amount_of_propeller = 1

        try:
            self.system_settings: SystemSettings = SystemSettings.get()
            self.sha_po_li = self.system_settings.sha_po_li
            self.amount_of_propeller = self.system_settings.amount_of_propeller
        except:
            pass


    def build(self):
        try:


            if self.amount_of_propeller == 1:
                if self.sha_po_li:
                    self.content = SingleShaPoLiOn()
                else:
                    self.content = SingleShaPoLiOff()
            elif self.amount_of_propeller == 2:
                if self.sha_po_li:
                    self.content = DualShaPoLiOn()
                else:
                    self.content = DualShaPoLiOff()
        except:
            logging.exception('exception occured at Dashboard.build')
