import logging
import flet as ft

from ui.common.keyboard import keyboard
from db.models.offline_default_value import OfflineDefaultValue
from ui.common.custom_card import CustomCard
from common.global_data import gdata
from utils.unit_converter import UnitConverter


class GeneralOflineDefaultValue(ft.Container):
    def __init__(self, system_unit: int):
        super().__init__()
        self.expand = True
        self.system_unit = system_unit

    def build(self):
        try:
            if self.page and self.page.session:
                self.torque_default_value = ft.TextField(
                    suffix_text="Nm",
                    label=self.page.session.get("lang.common.torque"),
                    value=gdata.configOffline.torque,
                    col={"xs": 6},
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, "int"))

                self.thrust_default_value = ft.TextField(
                    suffix_text="N",
                    label=self.page.session.get("lang.common.thrust"),
                    value=gdata.configOffline.thrust,
                    col={"xs": 6},
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, "int"))

                self.speed_default_value = ft.TextField(
                    suffix_text="rpm",
                    label=self.page.session.get("lang.common.speed"),
                    value=gdata.configOffline.speed,
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
        torque = int(self.torque_default_value.value)
        thrust = int(self.thrust_default_value.value)
        speed = float(self.speed_default_value.value)

        if self.system_unit == 0:
            torque = UnitConverter.knm_to_nm(torque)
            thrust = UnitConverter.kn_to_n(thrust)
        elif self.system_unit == 1:
            torque = UnitConverter.tm_to_nm(torque)
            thrust = UnitConverter.t_to_n(thrust)

        OfflineDefaultValue.update(torque_default_value=torque, thrust_default_value=thrust, speed_default_value=speed)
        gdata.configOffline.set_default_value()

    def update_unit(self, system_unit: int):
        try:
            self.system_unit = system_unit
            torque_default_value = int(gdata.configOffline.torque)
            thrust_default_value = int(gdata.configOffline.thrust)
            speed_default_value = float(gdata.configOffline.speed)

            if self.system_unit == 0:

                if self.torque_default_value is not None:
                    self.torque_default_value.suffix_text = "kNm"
                    self.torque_default_value.value = round(torque_default_value / 1000)

                if self.thrust_default_value is not None:
                    self.thrust_default_value.suffix_text = "kN"
                    self.thrust_default_value.value = round(thrust_default_value / 1000)

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
