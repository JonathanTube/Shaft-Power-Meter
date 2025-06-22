import logging
import flet as ft
from db.models.propeller_setting import PropellerSetting
from ui.common.keyboard import keyboard
from ui.common.custom_card import CustomCard
from ui.common.color_picker import ColorDialog


class PropellerConfNormalCurve(ft.Container):
    def __init__(self, ps: PropellerSetting):
        super().__init__()
        self.ps = ps

    def build(self):
        try:
            self.rpm_left_of_normal_propeller_curve = ft.TextField(
                label=self.page.session.get("lang.setting.rpm_left"), suffix_text='[%]',
                value=self.ps.rpm_left_of_normal_propeller_curve,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )
            self.bhp_left_of_normal_propeller_curve = ft.TextField(
                label=self.page.session.get("lang.setting.power_left"), suffix_text='[%]',
                value=self.ps.bhp_left_of_normal_propeller_curve,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )
            self.rpm_right_of_normal_propeller_curve = ft.TextField(
                label=self.page.session.get("lang.setting.rpm_right"), suffix_text='[%]',
                value=self.ps.rpm_right_of_normal_propeller_curve,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )
            self.bhp_right_of_normal_propeller_curve = ft.TextField(
                label=self.page.session.get("lang.setting.power_right"), suffix_text='[%]',
                value=self.ps.bhp_right_of_normal_propeller_curve,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )
            self.line_color_of_normal_propeller_curve = ColorDialog(color=self.ps.line_color_of_normal_propeller_curve)

            self.custom_card = CustomCard(
                self.page.session.get("lang.setting.normal_propeller_curve"),
                ft.ResponsiveRow(controls=[
                    self.rpm_left_of_normal_propeller_curve,
                    self.bhp_left_of_normal_propeller_curve,
                    self.rpm_right_of_normal_propeller_curve,
                    self.bhp_right_of_normal_propeller_curve,
                    self.line_color_of_normal_propeller_curve
                ]),
                col={"xs": 12})
            self.content = self.custom_card

        except:
            logging.exception('exception occured at PropellerConfNormalCurve.build')

    def save_data(self):
        self.ps.rpm_left_of_normal_propeller_curve = self.rpm_left_of_normal_propeller_curve.value
        self.ps.bhp_left_of_normal_propeller_curve = self.bhp_left_of_normal_propeller_curve.value
        self.ps.rpm_right_of_normal_propeller_curve = self.rpm_right_of_normal_propeller_curve.value
        self.ps.bhp_right_of_normal_propeller_curve = self.bhp_right_of_normal_propeller_curve.value
        self.ps.line_color_of_normal_propeller_curve = self.line_color_of_normal_propeller_curve.color
