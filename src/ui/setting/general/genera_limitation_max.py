import flet as ft

from db.models.limitations import Limitations
from ui.common.custom_card import CustomCard
from utils.unit_converter import UnitConverter
from ui.common.keyboard import keyboard
from db.models.opearation_log import OperationLog
from common.operation_type import OperationType
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict

class GeneralLimitationMax(ft.Container):
    def __init__(self, system_unit: int):
        super().__init__()
        self.expand = True
        self.col = {"md": 6}
        self.system_unit = system_unit
        self.limitations: Limitations = Limitations.get()

    def build(self):
        self.speed_max = ft.TextField(suffix_text="rpm",
                                      label=self.page.session.get("lang.common.speed"),
                                      value=self.limitations.speed_max,
                                      read_only=True,
                                      on_focus=lambda e: keyboard.open(e.control))

        self.torque_max = ft.TextField(suffix_text="kNm",
                                       label=self.page.session.get("lang.common.torque"),
                                       value=self.limitations.torque_max,
                                       read_only=True,
                                       on_focus=lambda e: keyboard.open(e.control))

        self.power_max = ft.TextField(suffix_text="kW",
                                      label=self.page.session.get("lang.common.power"),
                                      value=self.limitations.power_max,
                                      read_only=True,
                                      on_focus=lambda e: keyboard.open(e.control))

        self.content = CustomCard(
            self.page.session.get("lang.setting.maximum_limitations"),
            ft.Column(controls=[self.speed_max, self.torque_max, self.power_max])
        )

    def update_unit(self, system_unit: int):
        self.system_unit = system_unit
        torque_limit = self.limitations.torque_max
        power_limit = self.limitations.power_max
        if self.system_unit == 0:
            self.torque_max.suffix_text = "kNm"
            self.torque_max.value = round(torque_limit / 1000, 1)

            self.power_max.suffix_text = "kW"
            self.power_max.value = round(power_limit / 1000, 1)

        elif self.system_unit == 1:
            self.torque_max.suffix_text = "Tm"
            self.torque_max.value = UnitConverter.nm_to_tm(torque_limit)

            self.power_max.suffix_text = "sHp"
            self.power_max.value = UnitConverter.w_to_shp(power_limit)

        self.content.update()

    def save_data(self, user_id: int):
        # save limitations
        max_speed = float(self.speed_max.value or 0)
        max_torque = float(self.torque_max.value or 0)
        max_power = float(self.power_max.value or 0)

        if self.system_unit == 0:
            # kNm to Nm
            max_torque = UnitConverter.knm_to_nm(max_torque)
            # kw to w
            max_power = UnitConverter.kw_to_w(max_power)
        elif self.system_unit == 1:
            # Tm to Nm
            max_torque = UnitConverter.tm_to_nm(max_torque)
            # shp to w
            max_power = UnitConverter.shp_to_w(max_power)

        Limitations.update(
            power_max=max_power,
            torque_max=max_torque,
            speed_max=max_speed
        ).where(Limitations.id == self.limitations.id).execute()

        OperationLog.create(
            user_id=user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.GENERAL_LIMITATION_MAX,
            operation_content=model_to_dict(self.limitations)
        )
    def did_mount(self):
        self.update_unit(self.system_unit)
