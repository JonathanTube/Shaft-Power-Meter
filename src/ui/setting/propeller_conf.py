import flet as ft

from db.models.preference import Preference
from db.models.propeller_setting import PropellerSetting
from ui.common.color_picker import ColorDialog
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast
from utils.unit_converter import UnitConverter


class PropellerConf(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.alignment = ft.MainAxisAlignment.START
        # 这里有bug，如果添加了，外部页面就会居中
        self.scroll = ft.ScrollMode.ADAPTIVE

        self.system_unit = Preference.get().system_unit
        self.last_propeller_setting = PropellerSetting.get()

    def __get_shaft_power(self) -> tuple[float, str]:
        _shaft_power = self.last_propeller_setting.shaft_power_of_mcr_operating_point
        if self.system_unit == 0:
            return (_shaft_power / 1000, "kW")
        else:
            return (UnitConverter.w_to_hp(_shaft_power), "hp")

    def __create_mcr_operating_point(self):
        self.rpm_of_mcr_operating_point = ft.TextField(
            label="RPM",
            suffix_text='[1/min]',
            col={"md": 6},
            value=self.last_propeller_setting.rpm_of_mcr_operating_point,
            on_change=lambda e: setattr(
                self.last_propeller_setting, 'rpm_of_mcr_operating_point', e.control.value)
        )

        shaft_power_value, shaft_power_unit = self.__get_shaft_power()
        self.shaft_power_of_mcr_operating_point = ft.TextField(
            label="Shaft Power",
            col={"md": 6},
            value=shaft_power_value,
            suffix_text=shaft_power_unit,
            on_change=lambda e: setattr(
                self.last_propeller_setting, 'shaft_power_of_mcr_operating_point', e.control.value)
        )

        self.mcr_operating_point_card = CustomCard(
            'MCR Operating Point',
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
            label="RPM Left", suffix_text='[%]',
            value=self.last_propeller_setting.rpm_left_of_normal_propeller_curve,
            on_change=lambda e: setattr(
                self.last_propeller_setting, 'rpm_left_of_normal_propeller_curve', e.control.value)
        )
        self.bhp_left_of_normal_propeller_curve = ft.TextField(
            label="BHP Left", suffix_text='[%]',
            value=self.last_propeller_setting.bhp_left_of_normal_propeller_curve,
            on_change=lambda e: setattr(
                self.last_propeller_setting, 'bhp_left_of_normal_propeller_curve', e.control.value)
        )
        self.rpm_right_of_normal_propeller_curve = ft.TextField(
            label="RPM Right", suffix_text='[%]',
            value=self.last_propeller_setting.rpm_right_of_normal_propeller_curve,
            on_change=lambda e: setattr(
                self.last_propeller_setting, 'rpm_right_of_normal_propeller_curve', e.control.value)
        )
        self.bhp_right_of_normal_propeller_curve = ft.TextField(
            label="BHP Right", suffix_text='[%]',
            value=self.last_propeller_setting.bhp_right_of_normal_propeller_curve,
            on_change=lambda e: setattr(
                self.last_propeller_setting, 'bhp_right_of_normal_propeller_curve', e.control.value)
        )
        self.line_color_of_normal_propeller_curve = ColorDialog(
            on_change=lambda color: setattr(
                self.last_propeller_setting, 'line_color_of_normal_propeller_curve', color)
        )
        self.line_color_of_normal_propeller_curve.set_color(
            self.last_propeller_setting.line_color_of_normal_propeller_curve)

        self.normal_propeller_curve_card = CustomCard(
            'Normal Propeller Curve (1)',
            ft.Column(controls=[
                self.rpm_left_of_normal_propeller_curve,
                self.bhp_left_of_normal_propeller_curve,
                self.rpm_right_of_normal_propeller_curve,
                self.bhp_right_of_normal_propeller_curve,
                self.line_color_of_normal_propeller_curve.create()
            ])
        )

    def __create_light_propeller_curve(self):
        self.light_propeller_curve = ft.TextField(
            suffix_text="[% below (1)]",
            value=self.last_propeller_setting.value_of_light_propeller_curve,
            on_change=lambda e: setattr(
                self.last_propeller_setting,
                'value_of_light_propeller_curve',
                e.control.value
            )
        )
        self.line_color_of_light_propeller_curve = ColorDialog(
            on_change=lambda color: setattr(
                self.last_propeller_setting, 'line_color_of_light_propeller_curve', color)
        )
        self.line_color_of_light_propeller_curve.set_color(
            self.last_propeller_setting.line_color_of_light_propeller_curve
        )

        self.light_propeller_curve_card = CustomCard(
            'Light Propeller Curve (2)',
            ft.Column(controls=[self.light_propeller_curve,
                      self.line_color_of_light_propeller_curve.create()])
        )

    def __create_speed_limit_curve(self):
        self.speed_limit_curve = ft.TextField(
            suffix_text="[% MCR rpm]",
            value=self.last_propeller_setting.value_of_speed_limit_curve,
            on_change=lambda e: setattr(
                self.last_propeller_setting,
                'value_of_speed_limit_curve',
                e.control.value
            )
        )
        self.line_color_of_speed_limit_curve = ColorDialog(
            on_change=lambda color: setattr(
                self.last_propeller_setting, 'line_color_of_speed_limit_curve', color)
        )
        self.line_color_of_speed_limit_curve.set_color(
            self.last_propeller_setting.line_color_of_speed_limit_curve)

        self.speed_limit_curve_card = CustomCard(
            'Speed Limit Curve (3)',
            ft.Column(controls=[self.speed_limit_curve,
                      self.line_color_of_speed_limit_curve.create()])
        )

    def __create_torque_load_limit_curve(self):
        self.rpm_left_of_torque_load_limit_curve = ft.TextField(
            label="RPM Left", suffix_text='[%]',
            value=self.last_propeller_setting.rpm_left_of_torque_load_limit_curve,
            on_change=lambda e: setattr(
                self.last_propeller_setting, 'rpm_left_of_torque_load_limit_curve', e.control.value)
        )
        self.bhp_left_of_torque_load_limit_curve = ft.TextField(
            label="BHP Left", suffix_text='[%]',
            value=self.last_propeller_setting.bhp_left_of_torque_load_limit_curve,
            on_change=lambda e: setattr(self.last_propeller_setting, 'bhp_left_of_torque_load_limit_curve',
                                        e.control.value)
        )
        self.rpm_right_of_torque_load_limit_curve = ft.TextField(
            label="RPM Right", suffix_text='[%]',
            value=self.last_propeller_setting.rpm_right_of_torque_load_limit_curve,
            on_change=lambda e: setattr(self.last_propeller_setting, 'rpm_right_of_torque_load_limit_curve',
                                        e.control.value)
        )
        self.bhp_right_of_torque_load_limit_curve = ft.TextField(
            label="BHP Right", suffix_text='[%]',
            value=self.last_propeller_setting.bhp_right_of_torque_load_limit_curve,
            on_change=lambda e: setattr(self.last_propeller_setting, 'bhp_right_of_torque_load_limit_curve',
                                        e.control.value)
        )
        self.line_color_of_torque_load_limit_curve = ColorDialog(
            on_change=lambda color: setattr(
                self.last_propeller_setting, 'line_color_of_torque_load_limit_curve', color)
        )
        self.line_color_of_torque_load_limit_curve.set_color(
            self.last_propeller_setting.line_color_of_torque_load_limit_curve)

        self.torque_load_limit_curve_card = CustomCard(
            'Torque/Load Limit Curve (4)',
            ft.Column(controls=[
                self.rpm_left_of_torque_load_limit_curve,
                self.bhp_left_of_torque_load_limit_curve,
                self.rpm_right_of_torque_load_limit_curve,
                self.bhp_right_of_torque_load_limit_curve,
                self.line_color_of_torque_load_limit_curve.create()
            ])
        )

    def __create_overload_curve(self):
        self.overload_curve = ft.TextField(
            suffix_text="[% above (4)]", col={"md": 6},
            value=self.last_propeller_setting.value_of_overload_curve,
            on_change=lambda e: setattr(
                self.last_propeller_setting, 'value_of_overload_curve', e.control.value)
        )

        self.overload_alarm = ft.Switch(
            label="Overload Alarm", label_position=ft.LabelPosition.LEFT, col={"md": 6},
            value=self.last_propeller_setting.alarm_enabled_of_overload_curve,
            on_change=lambda e: setattr(
                self.last_propeller_setting, 'alarm_enabled_of_overload_curve', e.control.value)
        )

        self.line_color_of_overload_curve = ColorDialog(
            on_change=lambda color: setattr(
                self.last_propeller_setting, 'line_color_of_overload_curve', color)
        )
        self.line_color_of_overload_curve.set_color(
            self.last_propeller_setting.line_color_of_overload_curve)

        self.overload_curve_card = CustomCard(
            'Overload Curve (5)',
            ft.Column(
                controls=[
                    self.overload_curve,
                    self.overload_alarm,
                    self.line_color_of_overload_curve.create()
                ]
            ),
            col={"md": 6})

    def __save_data(self, e):
        _shaft_power = float(self.shaft_power_of_mcr_operating_point.value)
        if self.system_unit == 0:
            self.last_propeller_setting.shaft_power_of_mcr_operating_point = _shaft_power * 1000
        else:
            self.last_propeller_setting.shaft_power_of_mcr_operating_point = UnitConverter.hp_to_w(
                _shaft_power)
        self.last_propeller_setting.save()
        Toast.show_success(e.page)

    def __cancel_data(self, e):
        self.last_propeller_setting = PropellerSetting.select().order_by(
            PropellerSetting.id.desc()).first()

        self.rpm_of_mcr_operating_point.value = self.last_propeller_setting.rpm_of_mcr_operating_point
        shaft_power_value, shaft_power_unit = self.__get_shaft_power()
        self.shaft_power_of_mcr_operating_point.value = shaft_power_value
        self.shaft_power_of_mcr_operating_point.suffix_text = shaft_power_unit
        self.mcr_operating_point_card.update()

        self.rpm_left_of_normal_propeller_curve.value = self.last_propeller_setting.rpm_left_of_normal_propeller_curve
        self.bhp_left_of_normal_propeller_curve.value = self.last_propeller_setting.bhp_left_of_normal_propeller_curve
        self.rpm_right_of_normal_propeller_curve.value = self.last_propeller_setting.rpm_right_of_normal_propeller_curve
        self.bhp_right_of_normal_propeller_curve.value = self.last_propeller_setting.bhp_right_of_normal_propeller_curve
        self.line_color_of_normal_propeller_curve.set_color(
            self.last_propeller_setting.line_color_of_normal_propeller_curve)
        self.normal_propeller_curve_card.update()

        self.rpm_left_of_torque_load_limit_curve.value = self.last_propeller_setting.rpm_left_of_torque_load_limit_curve
        self.bhp_left_of_torque_load_limit_curve.value = self.last_propeller_setting.bhp_left_of_torque_load_limit_curve
        self.rpm_right_of_torque_load_limit_curve.value = self.last_propeller_setting.rpm_right_of_torque_load_limit_curve
        self.bhp_right_of_torque_load_limit_curve.value = self.last_propeller_setting.bhp_right_of_torque_load_limit_curve
        self.line_color_of_torque_load_limit_curve.set_color(
            self.last_propeller_setting.line_color_of_torque_load_limit_curve)
        self.torque_load_limit_curve_card.update()

        self.light_propeller_curve.value = self.last_propeller_setting.value_of_light_propeller_curve
        self.line_color_of_light_propeller_curve.set_color(
            self.last_propeller_setting.line_color_of_light_propeller_curve)
        self.light_propeller_curve_card.update()

        self.speed_limit_curve.value = self.last_propeller_setting.value_of_speed_limit_curve
        self.line_color_of_speed_limit_curve.set_color(
            self.last_propeller_setting.line_color_of_speed_limit_curve)
        self.speed_limit_curve_card.update()

        self.overload_curve.value = self.last_propeller_setting.value_of_overload_curve
        self.line_color_of_overload_curve.set_color(
            self.last_propeller_setting.line_color_of_overload_curve)
        self.overload_alarm.value = self.last_propeller_setting.alarm_enabled_of_overload_curve
        self.overload_curve_card.update()
        Toast.show_success(e.page)

    def build(self):
        self.__create_mcr_operating_point()
        self.__create_normal_propeller_curve()
        self.__create_torque_load_limit_curve()
        self.__create_light_propeller_curve()
        self.__create_speed_limit_curve()
        self.__create_overload_curve()

        self.save_button = ft.FilledButton(
            text="Save",
            width=120,
            height=40,
            on_click=lambda e: self.__save_data(e)
        )

        self.cancel_button = ft.OutlinedButton(
            text="Cancel",
            width=120,
            height=40,
            on_click=lambda e: self.__cancel_data(e)
        )

        self.controls = [
            ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.START,
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
                            self.cancel_button
                        ]
                    )
                ]
            )
        ]

    def __set_language(self):
        session = self.page.session

        self.mcr_operating_point_card.set_title(
            session.get("lang.setting.mcr_operating_point"))
        self.rpm_of_mcr_operating_point.label = session.get("lang.common.rpm")
        self.shaft_power_of_mcr_operating_point.label = session.get(
            "lang.common.power")

        self.normal_propeller_curve_card.set_title(
            session.get("lang.setting.normal_propeller_curve"))
        self.rpm_left_of_normal_propeller_curve.label = session.get(
            "lang.setting.rpm_left")
        self.bhp_left_of_normal_propeller_curve.label = session.get(
            "lang.setting.power_left")
        self.rpm_right_of_normal_propeller_curve.label = session.get(
            "lang.setting.rpm_right")
        self.bhp_right_of_normal_propeller_curve.label = session.get(
            "lang.setting.power_right")

        self.torque_load_limit_curve_card.set_title(
            session.get("lang.setting.torque_load_limit_curve"))
        self.rpm_left_of_torque_load_limit_curve.label = session.get(
            "lang.setting.rpm_left")
        self.bhp_left_of_torque_load_limit_curve.label = session.get(
            "lang.setting.power_left")
        self.rpm_right_of_torque_load_limit_curve.label = session.get(
            "lang.setting.rpm_right")
        self.bhp_right_of_torque_load_limit_curve.label = session.get(
            "lang.setting.power_right")

        self.light_propeller_curve_card.set_title(
            session.get("lang.setting.light_propeller_curve"))
        self.speed_limit_curve_card.set_title(
            session.get("lang.setting.speed_limit_curve"))
        self.overload_curve_card.set_title(
            session.get("lang.setting.overload_curve"))
        self.overload_alarm.label = session.get(
            "lang.setting.enable_overload_alarm")

        self.save_button.text = session.get("lang.button.save")
        self.cancel_button.text = session.get("lang.button.cancel")

    def before_update(self):
        self.__set_language()

    def did_mount(self):
        self.__set_language()
