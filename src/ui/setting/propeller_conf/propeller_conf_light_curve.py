import logging
import flet as ft
from ui.common.custom_card import CustomCard
from ui.common.color_picker import ColorDialog
from ui.common.keyboard import keyboard
from db.models.propeller_setting import PropellerSetting


class PropellerConfLightCurve(ft.Container):
    def __init__(self, ps: PropellerSetting):
        super().__init__()
        self.ps = ps

    def build(self):
        try:
            if self.page and self.page.session:
                self.light_propeller_curve = ft.TextField(
                    suffix_text="[% below (1)]",
                    value=self.ps.value_of_light_propeller_curve,
                    read_only=True,
                    col = {"xs": 6},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )
                self.line_color_of_light_propeller_curve = ColorDialog(color=self.ps.line_color_of_light_propeller_curve)

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.light_propeller_curve"),
                    ft.ResponsiveRow(controls=[
                        self.light_propeller_curve,
                        self.line_color_of_light_propeller_curve
                    ]),
                    col={"xs": 12})
                self.content = self.custom_card
        except:
            logging.exception('exception occured at PropellerConfLightCurve.build')

    def save_data(self):
        self.ps.value_of_light_propeller_curve = self.light_propeller_curve.value
        self.ps.line_color_of_light_propeller_curve = self.line_color_of_light_propeller_curve.color
