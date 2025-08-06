import logging
import flet as ft

from ui.common.keyboard import keyboard
from db.models.offline_default_value import OfflineDefaultValue
from ui.common.custom_card import CustomCard
from common.operation_type import OperationType
from db.models.operation_log import OperationLog
from common.global_data import gdata
from utils.unit_converter import UnitConverter


class GeneralOflineDefaultValue(ft.Container):
    def __init__(self, system_unit: int):
        super().__init__()
        self.expand = True
        self.system_unit = system_unit
        self.odv: OfflineDefaultValue = OfflineDefaultValue.get()

    def build(self):
        try:
            if self.page and self.page.session:
                self.torque_default_value = ft.TextField(
                    suffix_text="Nm",
                    label=self.page.session.get("lang.common.torque"),
                    value=self.odv.torque_default_value,
                    col={"xs": 6},
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control))

                self.thrust_default_value = ft.TextField(
                    suffix_text="N",
                    label=self.page.session.get("lang.common.thrust"),
                    value=self.odv.thrust_default_value,
                    col={"xs": 6},
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control))

                self.speed_default_value = ft.TextField(
                    suffix_text="rpm",
                    label=self.page.session.get("lang.common.speed"),
                    value=self.odv.speed_default_value,
                    col={"xs": 6},
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control))

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.offline_default_value"),
                    ft.ResponsiveRow(
                        controls=[
                            self.torque_default_value,
                            self.thrust_default_value,
                            self.speed_default_value
                        ]
                    )
                )

                self.content = self.custom_card
        except:
            logging.exception('exception occured at GeneralOflineDefaultValue.build')

    def before_update(self):
        try:
            if self.page and self.page.session:
                s = self.page.session
                if self.torque_default_value is not None:
                    self.torque_default_value.label = s.get("lang.common.torque")

                if self.thrust_default_value is not None:    
                    self.thrust_default_value.label = s.get("lang.common.thrust")

                if self.speed_default_value is not None:    
                    self.speed_default_value.label = s.get("lang.common.speed")

                if self.custom_card is not None:    
                    self.custom_card.set_title(s.get("lang.setting.offline_default_value"))
        except:
            logging.exception('exception occured at GeneralOflineDefaultValue.before_update')

    def save_data(self, user_id: int):
        if self.odv is None:
            return

        self.odv.torque_default_value = float(self.torque_default_value.value or 0)
        self.odv.thrust_default_value = float(self.thrust_default_value.value or 0)
        self.odv.speed_default_value = float(self.speed_default_value.value or 0)

        if self.system_unit == 0:
            self.odv.torque_default_value = UnitConverter.knm_to_nm(self.odv.torque_default_value)
            self.odv.thrust_default_value = UnitConverter.kn_to_n(self.odv.thrust_default_value)
        elif self.system_unit == 1:
            self.odv.torque_default_value = UnitConverter.tm_to_nm(self.odv.torque_default_value)
            self.odv.thrust_default_value = UnitConverter.t_to_n(self.odv.thrust_default_value)
        self.odv.save()

        gdata.configOffline.torque = self.odv.torque_default_value
        gdata.configOffline.speed = self.odv.speed_default_value
        gdata.configOffline.thrust = self.odv.thrust_default_value

        operation_log = OperationLog(
            user_id=user_id,
            utc_date_time=gdata.configDateTime.utc,
            operation_type=OperationType.OFFLINE_DEFAULT_VALUE,
            operation_content=f"update offline default value: {self.odv.torque_default_value}, {self.odv.thrust_default_value}, {self.odv.speed_default_value}"
        )
        operation_log.save()

    def update_unit(self, system_unit: int):
        try:
            self.system_unit = system_unit
            torque_default_value = float(self.odv.torque_default_value or 0)
            thrust_default_value = float(self.odv.thrust_default_value or 0)
            speed_default_value = float(self.odv.speed_default_value or 0)

            if self.system_unit == 0:

                if self.torque_default_value is not None:
                    self.torque_default_value.suffix_text = "kNm"
                    self.torque_default_value.value = round(torque_default_value / 1000, 1)

                if self.thrust_default_value is not None:
                    self.thrust_default_value.suffix_text = "kN"
                    self.thrust_default_value.value = round(thrust_default_value / 1000, 1)

                if self.speed_default_value is not None:
                    self.speed_default_value.suffix_text = "rpm"
                    self.speed_default_value.value = round(speed_default_value, 1)

            elif self.system_unit == 1:
                if self.torque_default_value is not None:
                    self.torque_default_value.suffix_text = "Tm"
                    self.torque_default_value.value = UnitConverter.nm_to_tm(torque_default_value)

                if self.thrust_default_value is not None:
                    self.thrust_default_value.suffix_text = "T"
                    self.thrust_default_value.value = UnitConverter.n_to_t(thrust_default_value)

                if self.speed_default_value is not None:
                    self.speed_default_value.suffix_text = "rpm"
                    self.speed_default_value.value = round(speed_default_value, 1)

            if self.content and self.content.page:
                self.content.update()
        except:
            logging.exception('exception occured at GeneralOflineDefaultValue.update_unit')

    def did_mount(self):
        self.update_unit(self.system_unit)
