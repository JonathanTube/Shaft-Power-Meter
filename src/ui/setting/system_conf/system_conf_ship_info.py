import flet as ft
import subprocess
from ui.common.custom_card import CustomCard
from db.models.ship_info import ShipInfo
from db.models.opearation_log import OperationLog
from common.operation_type import OperationType
from playhouse.shortcuts import model_to_dict
from common.global_data import gdata

class SystemConfShipInfo(CustomCard):
    def __init__(self):
        super().__init__()
        self.col = {'xs': 12}
        self.ship_info = ShipInfo.get()

    def build(self):
        self.ship_type = ft.TextField(
            label=self.page.session.get("lang.setting.ship_type"),
            value=self.ship_info.ship_type,
            on_click=lambda e: subprocess.run(["osk.exe"])
        )
        self.ship_name = ft.TextField(
            label=self.page.session.get("lang.setting.ship_name"),
            value=self.ship_info.ship_name,
            on_click=lambda e: subprocess.run(["osk.exe"])
        )
        self.imo_number = ft.TextField(
            label=self.page.session.get("lang.setting.imo_number"),
            value=self.ship_info.imo_number,
            on_click=lambda e: subprocess.run(["osk.exe"])
        )
        self.ship_size = ft.TextField(
            label=self.page.session.get("lang.setting.ship_size"),
            value=self.ship_info.ship_size,
            on_click=lambda e: subprocess.run(["osk.exe"])
        )

        self.heading = self.page.session.get("lang.setting.ship_info")
        self.body = ft.Column(controls=[
            self.ship_type,
            self.ship_name,
            self.imo_number,
            self.ship_size
        ])

        super().build()

    def save(self, user_id: int):
        self.ship_info.ship_type = self.ship_type.value
        self.ship_info.ship_name = self.ship_name.value
        self.ship_info.imo_number = self.imo_number.value
        self.ship_info.ship_size = self.ship_size.value
        self.ship_info.save()
        OperationLog.create(
            user_id=user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.SYSTEM_CONF_SHIP_INFO,
            operation_content=model_to_dict(self.ship_info)
        )
