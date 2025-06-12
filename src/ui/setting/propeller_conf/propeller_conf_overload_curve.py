import flet as ft
from ui.common.custom_card import CustomCard
from db.models.propeller_setting import PropellerSetting
from ui.common.color_picker import ColorDialog
from ui.common.keyboard import keyboard
from common.global_data import gdata


class PropellerConfOverloadCurve(CustomCard):
    def __init__(self, ps: PropellerSetting):
        super().__init__()
        self.ps = ps

    def build(self):
        self.overload_curve = ft.TextField(
            suffix_text="[% above (4)]", col={"md": 6},
            value=self.ps.value_of_overload_curve,
            read_only=True,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control)
        )

        self.overload_alarm = ft.Checkbox(label=self.page.session.get("lang.setting.enable_overload_alarm"), col={"md": 6}, value=self.ps.alarm_enabled_of_overload_curve)

        self.line_color_of_overload_curve = ColorDialog(color=self.ps.line_color_of_overload_curve)

        self.heading = self.page.session.get("lang.setting.overload_curve")
        self.body = ft.Column(controls=[
            self.overload_curve,
            self.overload_alarm,
            self.line_color_of_overload_curve
        ])

        super().build()

    def save_data(self):
        self.ps.value_of_overload_curve = self.overload_curve.value
        self.ps.alarm_enabled_of_overload_curve = self.overload_alarm.value
        self.ps.line_color_of_overload_curve = self.line_color_of_overload_curve.color

        gdata.power_of_overload = self.ps.value_of_overload_curve
