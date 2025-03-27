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
        self.system_settings = SystemSettings.get_or_none()

    def build(self):
        if self.system_settings is None:
            sha_po_li = False
            amount_of_power = 1
        else:
            sha_po_li = self.system_settings.sha_po_li
            amount_of_power = self.system_settings.amount_of_propeller

        print('amount_of_power=', amount_of_power, 'sha_po_li=', sha_po_li)

        if amount_of_power == 1:
            self.content = SingleShaPoLiOn() if sha_po_li else SingleShaPoLiOff()
        elif amount_of_power == 2:
            self.content = DualShaPoLiOn() if sha_po_li else DualShaPoLiOff()
