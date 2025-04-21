import flet as ft
from ui.common.custom_card import CustomCard
from db.models.ship_info import ShipInfo


class SystemConfShipInfo(CustomCard):
    def __init__(self):
        super().__init__()
        self.ship_info = ShipInfo.get()

    def build(self):
        self.ship_type = ft.TextField(
            label=self.page.session.get("lang.setting.ship_type"),
            value=self.ship_info.ship_type
        )
        self.ship_name = ft.TextField(
            label=self.page.session.get("lang.setting.ship_name"),
            value=self.ship_info.ship_name
        )
        self.imo_number = ft.TextField(
            label=self.page.session.get("lang.setting.imo_number"),
            value=self.ship_info.imo_number
        )
        self.ship_size = ft.TextField(
            label=self.page.session.get("lang.setting.ship_size"),
            value=self.ship_info.ship_size
        )

        self.heading = self.page.session.get("lang.setting.ship_info")
        self.body = ft.Column(controls=[
            self.ship_type,
            self.ship_name,
            self.imo_number,
            self.ship_size
        ])
        self.height = 360

        super().build()

    def save(self):
        self.ship_info.ship_type = self.ship_type.value
        self.ship_info.ship_name = self.ship_name.value
        self.ship_info.imo_number = self.imo_number.value
        self.ship_info.ship_size = self.ship_size.value
        self.ship_info.save()
