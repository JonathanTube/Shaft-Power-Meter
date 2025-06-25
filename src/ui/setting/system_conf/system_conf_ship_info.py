import logging
import flet as ft
from db.models.user import User
from ui.common.custom_card import CustomCard
from db.models.ship_info import ShipInfo
from db.models.operation_log import OperationLog
from common.operation_type import OperationType
from playhouse.shortcuts import model_to_dict
from common.global_data import gdata


class SystemConfShipInfo(ft.Container):
    def __init__(self):
        super().__init__()
        self.col = {'xs': 12}
        self.ship_info: ShipInfo = ShipInfo.get()

    def build(self):
        try:
            if self.page and self.page.session:
                self.ship_type = ft.TextField(
                    label=self.page.session.get("lang.setting.ship_type"),
                    value=self.ship_info.ship_type,
                    col={'xs': 6}
                )
                self.ship_name = ft.TextField(
                    label=self.page.session.get("lang.setting.ship_name"),
                    value=self.ship_info.ship_name,
                    col={'xs': 6}
                )
                self.imo_number = ft.TextField(
                    label=self.page.session.get("lang.setting.imo_number"),
                    value=self.ship_info.imo_number,
                    col={'xs': 6}
                )
                self.ship_size = ft.TextField(
                    label=self.page.session.get("lang.setting.ship_size"),
                    value=self.ship_info.ship_size,
                    col={'xs': 6}
                )

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.ship_info"),
                    ft.ResponsiveRow(controls=[
                        self.ship_type,
                        self.ship_name,
                        self.imo_number,
                        self.ship_size
                    ]),
                    col={"xs": 12})
                self.content = self.custom_card
        except:
            logging.exception('exception occured at SystemConfShipInfo.build')

    def save(self, user: User):
        # 不要处理异常，外部已经catch
        self.ship_info.ship_type = self.ship_type.value
        self.ship_info.ship_name = self.ship_name.value
        self.ship_info.imo_number = self.imo_number.value
        self.ship_info.ship_size = self.ship_size.value
        self.ship_info.save()
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.SYSTEM_CONF_SHIP_INFO,
            operation_content=model_to_dict(self.ship_info)
        )
