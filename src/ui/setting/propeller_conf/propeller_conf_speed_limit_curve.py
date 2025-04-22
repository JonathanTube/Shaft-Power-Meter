import flet as ft
from ui.common.custom_card import CustomCard
from db.models.propeller_setting import PropellerSetting
from ui.common.color_picker import ColorDialog
from ui.common.keyboard import keyboard


class PropellerConfSpeedLimitCurve(CustomCard):
    def __init__(self, ps: PropellerSetting):
        super().__init__()
        self.ps = ps

    def build(self):
        self.speed_limit_curve = ft.TextField(
            suffix_text="[% MCR rpm]",
            value=self.ps.value_of_speed_limit_curve,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.line_color_of_speed_limit_curve = ColorDialog(color=self.ps.line_color_of_speed_limit_curve)

        self.heading = self.page.session.get("lang.setting.speed_limit_curve")
        self.body = ft.Column(controls=[
            self.speed_limit_curve,
            self.line_color_of_speed_limit_curve
        ])

        super().build()

    def save_data(self):
        self.ps.value_of_speed_limit_curve = self.speed_limit_curve.value
        self.ps.line_color_of_speed_limit_curve = self.line_color_of_speed_limit_curve.color
