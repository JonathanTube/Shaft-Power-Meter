import flet as ft
from common.global_data import gdata
from ui.common.custom_card import CustomCard
from ui.common.color_picker import ColorDialog
from ui.common.keyboard import keyboard
from db.models.propeller_setting import PropellerSetting


class PropellerConfLimitCurve(CustomCard):
    def __init__(self, ps: PropellerSetting):
        super().__init__()
        self.ps = ps

    def build(self):
        self.rpm_left_of_torque_load_limit_curve = ft.TextField(
            label=self.page.session.get("lang.setting.rpm_left"), suffix_text='[%]',
            value=self.ps.rpm_left_of_torque_load_limit_curve,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.bhp_left_of_torque_load_limit_curve = ft.TextField(
            label=self.page.session.get("lang.setting.power_left"), suffix_text='[%]',
            value=self.ps.bhp_left_of_torque_load_limit_curve,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.rpm_right_of_torque_load_limit_curve = ft.TextField(
            label=self.page.session.get("lang.setting.rpm_right"), suffix_text='[%]',
            value=self.ps.rpm_right_of_torque_load_limit_curve,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.bhp_right_of_torque_load_limit_curve = ft.TextField(
            label=self.page.session.get("lang.setting.power_right"), suffix_text='[%]',
            value=self.ps.bhp_right_of_torque_load_limit_curve,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.line_color_of_torque_load_limit_curve = ColorDialog(
            color=self.ps.line_color_of_torque_load_limit_curve
        )

        self.heading = self.page.session.get("lang.setting.torque_load_limit_curve")
        self.body = ft.Column(controls=[
            self.rpm_left_of_torque_load_limit_curve,
            self.bhp_left_of_torque_load_limit_curve,
            self.rpm_right_of_torque_load_limit_curve,
            self.bhp_right_of_torque_load_limit_curve,
            self.line_color_of_torque_load_limit_curve
        ])

        super().build()

    def save_data(self):
        self.ps.rpm_left_of_torque_load_limit_curve = self.rpm_left_of_torque_load_limit_curve.value
        self.ps.bhp_left_of_torque_load_limit_curve = self.bhp_left_of_torque_load_limit_curve.value
        self.ps.rpm_right_of_torque_load_limit_curve = self.rpm_right_of_torque_load_limit_curve.value
        self.ps.bhp_right_of_torque_load_limit_curve = self.bhp_right_of_torque_load_limit_curve.value
        self.ps.line_color_of_torque_load_limit_curve = self.line_color_of_torque_load_limit_curve.color

        gdata.speed_of_torque_load_limit = float(self.ps.rpm_right_of_torque_load_limit_curve)
        gdata.power_of_torque_load_limit = float(self.ps.bhp_right_of_torque_load_limit_curve)
