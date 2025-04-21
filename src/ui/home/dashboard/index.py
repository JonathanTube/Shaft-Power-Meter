import flet as ft

from common.public_controls import PublicControls
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

        # print('amount_of_power=', amount_of_power, 'sha_po_li=', sha_po_li)

        if amount_of_power == 1:
            if sha_po_li:
                self.content = SingleShaPoLiOn()
                PublicControls.sps_single_on = self.content
            else:
                self.content = SingleShaPoLiOff()
                PublicControls.sps_single_off = self.content
        elif amount_of_power == 2:
            if sha_po_li:
                self.content = DualShaPoLiOn()
                PublicControls.sps_dual_on = self.content
            else:
                self.content = DualShaPoLiOff()
                PublicControls.sps_dual_off = self.content

    def will_unmount(self):
        PublicControls.sps_single_on = None
        PublicControls.sps_single_off = None
        PublicControls.sps_dual_on = None
        PublicControls.sps_dual_off = None
