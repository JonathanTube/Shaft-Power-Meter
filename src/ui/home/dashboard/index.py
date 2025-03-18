import flet as ft

from ui.home.dashboard.fixed_right import FixedRight
from ui.home.dashboard.power_chart import PowerChart
from ui.home.dashboard.single.shapoli_off import DashboardShaPoLiOff
from ui.home.dashboard.single.shapoli_on import DashboardShaPoLiOn
from db.models.system_settings import SystemSettings


class Dashboard(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.only(left=10, right=10, top=10, bottom=10)
        self.system_settings = SystemSettings.select().order_by(
            SystemSettings.id.desc()).first()
        self.content = self.__create()

    def __create(self):
        if self.system_settings is not None and self.system_settings.sha_po_li:
            self.dashboard = DashboardShaPoLiOn()
        else:
            self.dashboard = DashboardShaPoLiOff()

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
