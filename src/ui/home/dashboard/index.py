import flet as ft

from common.control_manager import ControlManager
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

        if amount_of_power == 1:
            if sha_po_li:
                self.content = SingleShaPoLiOn()
                ControlManager.sps_single_on = self.content
            else:
                self.content = SingleShaPoLiOff()
                ControlManager.sps_single_off = self.content
        elif amount_of_power == 2:
            if sha_po_li:
                self.content = DualShaPoLiOn()
                ControlManager.sps_dual_on = self.content
            else:
                self.content = DualShaPoLiOff()
                ControlManager.sps_dual_off = self.content

    def will_unmount(self):
        ControlManager.sps_single_on = None
        ControlManager.sps_single_off = None
        ControlManager.sps_dual_on = None
        ControlManager.sps_dual_off = None
