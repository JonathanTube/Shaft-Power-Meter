import flet as ft

from common.const_pubsub_topic import PubSubTopic
from db.models.preference import Preference
from db.models.propeller_setting import PropellerSetting
from ui.common.color_picker import ColorDialog
from ui.common.custom_card import CustomCard
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from utils.unit_converter import UnitConverter
from common.global_data import gdata


class PropellerConf(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.alignment = ft.alignment.top_left

        self.system_unit: Preference = Preference.get().system_unit
        self.propeller_setting: PropellerSetting = PropellerSetting.get()

    def __get_shaft_power(self) -> tuple[float, str]:
        _shaft_power = self.propeller_setting.shaft_power_of_mcr_operating_point
        if self.system_unit == 0:
            return (_shaft_power / 1000, "kW")
        else:
            return (UnitConverter.w_to_shp(_shaft_power), "hp")

    def __set_shaft_power(self, e):
        _shaft_power = float(e.control.value)
        if self.system_unit == 0:
            self.propeller_setting.shaft_power_of_mcr_operating_point = _shaft_power * 1000
        else:
            self.propeller_setting.shaft_power_of_mcr_operating_point = UnitConverter.shp_to_w(
                _shaft_power)

    def __create_mcr_operating_point(self):
        self.rpm_of_mcr_operating_point = ft.TextField(
            label=self.page.session.get("lang.common.speed"),
            suffix_text='rpm',
            col={"md": 6},
            value=self.propeller_setting.rpm_of_mcr_operating_point,
            on_change=lambda e: setattr(
                self.propeller_setting, 'rpm_of_mcr_operating_point', e.control.value)
        )

        shaft_power_value, shaft_power_unit = self.__get_shaft_power()
        self.shaft_power_of_mcr_operating_point = ft.TextField(
            label=self.page.session.get("lang.common.power"),
            col={"md": 6},
            value=shaft_power_value,
            suffix_text=shaft_power_unit,
            on_change=self.__set_shaft_power
        )

        self.mcr_operating_point_card = CustomCard(
            self.page.session.get("lang.setting.mcr_operating_point"),
            ft.ResponsiveRow(
                spacing=20,
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    self.rpm_of_mcr_operating_point,
                    self.shaft_power_of_mcr_operating_point
                ]
            ),
            col={"xs": 12}
        )

    def __create_normal_propeller_curve(self):
        self.rpm_left_of_normal_propeller_curve = ft.TextField(
            label=self.page.session.get("lang.setting.rpm_left"), suffix_text='[%]',
            value=self.propeller_setting.rpm_left_of_normal_propeller_curve,
            on_change=lambda e: setattr(
                self.propeller_setting, 'rpm_left_of_normal_propeller_curve', e.control.value)
        )
        self.bhp_left_of_normal_propeller_curve = ft.TextField(
            label=self.page.session.get("lang.setting.power_left"), suffix_text='[%]',
            value=self.propeller_setting.bhp_left_of_normal_propeller_curve,
            on_change=lambda e: setattr(
                self.propeller_setting, 'bhp_left_of_normal_propeller_curve', e.control.value)
        )
        self.rpm_right_of_normal_propeller_curve = ft.TextField(
            label=self.page.session.get("lang.setting.rpm_right"), suffix_text='[%]',
            value=self.propeller_setting.rpm_right_of_normal_propeller_curve,
            on_change=lambda e: setattr(
                self.propeller_setting, 'rpm_right_of_normal_propeller_curve', e.control.value)
        )
        self.bhp_right_of_normal_propeller_curve = ft.TextField(
            label=self.page.session.get("lang.setting.power_right"), suffix_text='[%]',
            value=self.propeller_setting.bhp_right_of_normal_propeller_curve,
            on_change=lambda e: setattr(
                self.propeller_setting, 'bhp_right_of_normal_propeller_curve', e.control.value)
        )
        self.line_color_of_normal_propeller_curve = ColorDialog(
            color=self.propeller_setting.line_color_of_normal_propeller_curve,
            on_change=lambda color: setattr(
                self.propeller_setting, 'line_color_of_normal_propeller_curve', color)
        )

        self.normal_propeller_curve_card = CustomCard(
            self.page.session.get("lang.setting.normal_propeller_curve"),
            ft.Column(controls=[
                self.rpm_left_of_normal_propeller_curve,
                self.bhp_left_of_normal_propeller_curve,
                self.rpm_right_of_normal_propeller_curve,
                self.bhp_right_of_normal_propeller_curve,
                self.line_color_of_normal_propeller_curve
            ])
        )

    def __create_light_propeller_curve(self):
        self.light_propeller_curve = ft.TextField(
            suffix_text="[% below (1)]",
            value=self.propeller_setting.value_of_light_propeller_curve,
            on_change=lambda e: setattr(
                self.propeller_setting,
                'value_of_light_propeller_curve',
                e.control.value
            )
        )
        self.line_color_of_light_propeller_curve = ColorDialog(
            color=self.propeller_setting.line_color_of_light_propeller_curve,
            on_change=lambda color: setattr(
                self.propeller_setting, 'line_color_of_light_propeller_curve', color)
        )

        self.light_propeller_curve_card = CustomCard(
            self.page.session.get("lang.setting.light_propeller_curve"),
            ft.Column(controls=[self.light_propeller_curve,
                      self.line_color_of_light_propeller_curve])
        )

    def __create_speed_limit_curve(self):
        self.speed_limit_curve = ft.TextField(
            suffix_text="[% MCR rpm]",
            value=self.propeller_setting.value_of_speed_limit_curve,
            on_change=lambda e: setattr(
                self.propeller_setting,
                'value_of_speed_limit_curve',
                e.control.value
            )
        )
        self.line_color_of_speed_limit_curve = ColorDialog(
            color=self.propeller_setting.line_color_of_speed_limit_curve,
            on_change=lambda color: setattr(
                self.propeller_setting, 'line_color_of_speed_limit_curve', color)
        )

        self.speed_limit_curve_card = CustomCard(
            self.page.session.get("lang.setting.speed_limit_curve"),
            ft.Column(controls=[self.speed_limit_curve,
                      self.line_color_of_speed_limit_curve])
        )

    def __create_torque_load_limit_curve(self):
        self.rpm_left_of_torque_load_limit_curve = ft.TextField(
            label=self.page.session.get("lang.setting.rpm_left"), suffix_text='[%]',
            value=self.propeller_setting.rpm_left_of_torque_load_limit_curve,
            on_change=lambda e: setattr(
                self.propeller_setting, 'rpm_left_of_torque_load_limit_curve', e.control.value)
        )
        self.bhp_left_of_torque_load_limit_curve = ft.TextField(
            label=self.page.session.get("lang.setting.power_left"), suffix_text='[%]',
            value=self.propeller_setting.bhp_left_of_torque_load_limit_curve,
            on_change=lambda e: setattr(self.propeller_setting, 'bhp_left_of_torque_load_limit_curve',
                                        e.control.value)
        )
        self.rpm_right_of_torque_load_limit_curve = ft.TextField(
            label=self.page.session.get("lang.setting.rpm_right"), suffix_text='[%]',
            value=self.propeller_setting.rpm_right_of_torque_load_limit_curve,
            on_change=lambda e: setattr(self.propeller_setting, 'rpm_right_of_torque_load_limit_curve',
                                        e.control.value)
        )
        self.bhp_right_of_torque_load_limit_curve = ft.TextField(
            label=self.page.session.get("lang.setting.power_right"), suffix_text='[%]',
            value=self.propeller_setting.bhp_right_of_torque_load_limit_curve,
            on_change=lambda e: setattr(self.propeller_setting, 'bhp_right_of_torque_load_limit_curve',
                                        e.control.value)
        )
        self.line_color_of_torque_load_limit_curve = ColorDialog(
            color=self.propeller_setting.line_color_of_torque_load_limit_curve,
            on_change=lambda color: setattr(
                self.propeller_setting, 'line_color_of_torque_load_limit_curve', color)
        )

        self.torque_load_limit_curve_card = CustomCard(
            self.page.session.get("lang.setting.torque_load_limit_curve"),
            ft.Column(controls=[
                self.rpm_left_of_torque_load_limit_curve,
                self.bhp_left_of_torque_load_limit_curve,
                self.rpm_right_of_torque_load_limit_curve,
                self.bhp_right_of_torque_load_limit_curve,
                self.line_color_of_torque_load_limit_curve
            ])
        )

    def __create_overload_curve(self):
        self.overload_curve = ft.TextField(
            suffix_text="[% above (4)]", col={"md": 6},
            value=self.propeller_setting.value_of_overload_curve,
            on_change=lambda e: setattr(
                self.propeller_setting, 'value_of_overload_curve', e.control.value)
        )

        self.overload_alarm = ft.Switch(
            label=self.page.session.get("lang.setting.enable_overload_alarm"), label_position=ft.LabelPosition.LEFT, col={"md": 6},
            value=self.propeller_setting.alarm_enabled_of_overload_curve,
            on_change=lambda e: setattr(
                self.propeller_setting, 'alarm_enabled_of_overload_curve', e.control.value)
        )

        self.line_color_of_overload_curve = ColorDialog(
            color=self.propeller_setting.line_color_of_overload_curve,
            on_change=lambda color: setattr(
                self.propeller_setting, 'line_color_of_overload_curve', color)
        )

        self.overload_curve_card = CustomCard(
            self.page.session.get("lang.setting.overload_curve"),
            ft.Column(
                controls=[
                    self.overload_curve,
                    self.overload_alarm,
                    self.line_color_of_overload_curve
                ]
            ),
            col={"md": 6})

    def __on_save_button_click(self, e):
        self.page.open(PermissionCheck(self.__save_data, 2))

    def __save_data(self):
        if self.propeller_setting.alarm_enabled_of_overload_curve:
            gdata.enable_power_overload_alarm = True
        else:
            gdata.enable_power_overload_alarm = False

        self.propeller_setting.save()
        Toast.show_success(self.page)

    def __reset_data(self, e):
        self.propeller_setting = PropellerSetting.get()
        self.content.clean()
        self.build()
        Toast.show_success(e.page)

    def build(self):
        self.__create_mcr_operating_point()
        self.__create_normal_propeller_curve()
        self.__create_torque_load_limit_curve()
        self.__create_light_propeller_curve()
        self.__create_speed_limit_curve()
        self.__create_overload_curve()

        self.save_button = ft.FilledButton(
            self.page.session.get("lang.button.save"),
            width=120,
            height=40,
            on_click=lambda e: self.__on_save_button_click(e)
        )

        self.reset_button = ft.OutlinedButton(
            self.page.session.get("lang.button.reset"),
            width=120,
            height=40,
            on_click=lambda e: self.__reset_data(e)
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                ft.ResponsiveRow(
                    controls=[
                        self.mcr_operating_point_card,
                        self.normal_propeller_curve_card,
                        self.torque_load_limit_curve_card,
                        self.light_propeller_curve_card,
                        self.speed_limit_curve_card,
                        self.overload_curve_card,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                self.save_button,
                                self.reset_button
                            ]
                        )
                    ]
                )
            ]
        )
