import flet as ft

from ui.home.dashboard.dual.dual_shapoli_off import DualShaPoLiOff
from ui.home.dashboard.dual.dual_shapoli_on import DualShaPoLiOn
from ui.home.dashboard.fixed_right import FixedRight
from ui.home.dashboard.power_chart import PowerChart
from ui.home.dashboard.single.single_shapoli_off import SingleShaPoLiOff
from ui.home.dashboard.single.single_shapoli_on import SingleShaPoLiOn
from db.models.system_settings import SystemSettings


class Dashboard(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.only(left=10, right=10, top=10, bottom=10)
        self.system_settings = SystemSettings.select().order_by(
            SystemSettings.id.desc()).first()
        self.content = self.__create()

    def __create(self):
        print(self.system_settings)
        if self.system_settings is None:
            sha_po_li = False
            amount_of_power = 1
        else:
            sha_po_li = self.system_settings.sha_po_li
            amount_of_power = self.system_settings.amount_of_propeller

        if amount_of_power == 1:
            self.dashboard = SingleShaPoLiOn() if sha_po_li else SingleShaPoLiOff()
        elif amount_of_power == 2:
            self.dashboard = DualShaPoLiOn() if sha_po_li else DualShaPoLiOff()

        main_content = ft.Column(
            expand=True,
            spacing=20,
            controls=[self.dashboard, PowerChart()]
        )

        fixed_right = FixedRight()

        return ft.Stack(
            # expand=True,
            controls=[
                main_content,
                # This is the fixed right content, must be placed at the end of the main_content, otherwise it will be covered by the main_content
                fixed_right
            ]
        )
