import flet as ft

from ui.home.dashboard.dual.dual_shapoli_off import DualShaPoLiOff
from ui.home.dashboard.dual.dual_shapoli_on import DualShaPoLiOn
from ui.home.dashboard.single.off.single_shapoli_off import SingleShaPoLiOff
from ui.home.dashboard.single.on.single_shapoli_on import SingleShaPoLiOn
from db.models.system_settings import SystemSettings


class Dashboard(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.only(left=10, right=10, top=10, bottom=10)
        self.system_settings = SystemSettings.get_or_none()

    def build(self):
        if self.system_settings is None:
            sha_po_li = False
            amount_of_power = 1
        else:
            sha_po_li = self.system_settings.sha_po_li
            amount_of_power = self.system_settings.amount_of_propeller

        if amount_of_power == 1:
            self.content = SingleShaPoLiOn() if sha_po_li else SingleShaPoLiOff()
        elif amount_of_power == 2:
            self.content = DualShaPoLiOn() if sha_po_li else DualShaPoLiOff()
