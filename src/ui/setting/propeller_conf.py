import flet as ft

from db.models.propeller_setting import PropellerSetting
from ui.common.color_picker import ColorDialog
from ui.common.custom_card import create_card
from ui.common.toast import Toast


class PropellerConf:
    def __init__(self):
        self.last_propeller_setting = PropellerSetting.select().order_by(PropellerSetting.id.desc()).first()
        if self.last_propeller_setting is None:
            self.last_propeller_setting = PropellerSetting.create(
                rpm_of_mcr_operating_point=0,
                shaft_power_of_mcr_operating_point=0,

                rpm_left_of_normal_propeller_curve=0,
                bhp_left_of_normal_propeller_curve=0,
                rpm_right_of_normal_propeller_curve=0,
                bhp_right_of_normal_propeller_curve=0,
                line_color_of_normal_propeller_curve='c8df6f',

                value_of_light_propeller_curve=0,
                line_color_of_light_propeller_curve='c8df6f',

                value_of_speed_limit_curve=0,
                line_color_of_speed_limit_curve='c8df6f',

                rpm_left_of_torque_load_limit_curve=0,
                bhp_left_of_torque_load_limit_curve=0,
                rpm_right_of_torque_load_limit_curve=0,
                bhp_right_of_torque_load_limit_curve=0,
                line_color_of_torque_load_limit_curve='c8df6f',

                value_of_overload_curve=0,
                line_color_of_overload_curve='c8df6f',
                alarm_enabled_of_overload_curve=0
            )

    def __create_mcr_operating_point(self):
        self.rpm_of_mcr_operating_point = ft.TextField(
            label="RPM",
            suffix_text='[1/min]',
            col={"md": 6},
            value=self.last_propeller_setting.rpm_of_mcr_operating_point,
            on_change=lambda e: setattr(self.last_propeller_setting,'rpm_of_mcr_operating_point', e.control.value)
        )

        self.shaft_power_of_mcr_operating_point = ft.TextField(
            label="Shaft Power",
            suffix_text='[kW]',
            col={"md": 6},
            value=self.last_propeller_setting.shaft_power_of_mcr_operating_point,
            on_change=lambda e: setattr(self.last_propeller_setting,'shaft_power_of_mcr_operating_point', e.control.value)
        )

        self.mcr_operating_point_card = create_card(
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
            on_change=lambda e: setattr(self.last_propeller_setting,'rpm_left_of_normal_propeller_curve', e.control.value)
        )
        self.bhp_left_of_normal_propeller_curve = ft.TextField(
            label="BHP Left", suffix_text='[%]',
            value=self.last_propeller_setting.bhp_left_of_normal_propeller_curve,
            on_change=lambda e: setattr(self.last_propeller_setting,'bhp_left_of_normal_propeller_curve', e.control.value)
        )
        self.rpm_right_of_normal_propeller_curve = ft.TextField(
            label="RPM Right", suffix_text='[%]',
            value=self.last_propeller_setting.rpm_right_of_normal_propeller_curve,
            on_change=lambda e: setattr(self.last_propeller_setting,'rpm_right_of_normal_propeller_curve', e.control.value)
        )
        self.bhp_right_of_normal_propeller_curve = ft.TextField(
            label="BHP Right", suffix_text='[%]',
            value=self.last_propeller_setting.bhp_right_of_normal_propeller_curve,
            on_change=lambda e: setattr(self.last_propeller_setting,'bhp_right_of_normal_propeller_curve', e.control.value)
        )
        self.line_color_of_normal_propeller_curve = ColorDialog(
            on_change=lambda color: setattr(self.last_propeller_setting,'line_color_of_normal_propeller_curve', color)
        )
        self.line_color_of_normal_propeller_curve.set_color(self.last_propeller_setting.line_color_of_normal_propeller_curve)

        self.normal_propeller_curve_card = create_card(
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
            label="Light", suffix_text="[% below (1)]",
            value=self.last_propeller_setting.value_of_light_propeller_curve,
            on_change=lambda e: setattr(self.last_propeller_setting,'value_of_light_propeller_curve', e.control.value)
        )
        self.line_color_of_light_propeller_curve = ColorDialog(
            on_change=lambda color: setattr(self.last_propeller_setting,'line_color_of_light_propeller_curve', color)
        )
        self.line_color_of_light_propeller_curve.set_color(
            self.last_propeller_setting.line_color_of_light_propeller_curve
        )

        self.light_propeller_curve_card = create_card(
            'Light Propeller Curve (2)',
            ft.Column(controls=[self.light_propeller_curve, self.line_color_of_light_propeller_curve.create()])
        )

    def __create_speed_limit_curve(self):
        self.speed_limit_curve = ft.TextField(
            label="Limit", suffix_text="[% MCR rpm]",
            value=self.last_propeller_setting.value_of_speed_limit_curve,
            on_change=lambda e: setattr(self.last_propeller_setting,'value_of_speed_limit_curve',e.control.value)
        )
        self.line_color_of_speed_limit_curve = ColorDialog(
            on_change=lambda color: setattr(self.last_propeller_setting,'line_color_of_speed_limit_curve', color)
        )
        self.line_color_of_speed_limit_curve.set_color(self.last_propeller_setting.line_color_of_speed_limit_curve)

        self.speed_limit_curve_card = create_card(
            'Speed Limit Curve (3)',
            ft.Column(controls=[self.speed_limit_curve, self.line_color_of_speed_limit_curve.create()])
        )

    def __create_torque_load_limit_curve(self):
        self.rpm_left_of_torque_load_limit_curve = ft.TextField(
            label="RPM Left", suffix_text='[%]',
            value=self.last_propeller_setting.rpm_left_of_torque_load_limit_curve,
            on_change=lambda e: setattr(self.last_propeller_setting, 'rpm_left_of_torque_load_limit_curve', e.control.value)
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
            on_change=lambda color: setattr(self.last_propeller_setting,'line_color_of_torque_load_limit_curve', color)
        )
        self.line_color_of_torque_load_limit_curve.set_color(self.last_propeller_setting.line_color_of_torque_load_limit_curve)

        self.torque_load_limit_curve_card = create_card(
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
            label="Overload", suffix_text="[% above (4)]", col={"md": 6},
            value=self.last_propeller_setting.value_of_overload_curve,
            on_change=lambda e: setattr(self.last_propeller_setting, 'value_of_overload_curve', e.control.value)
        )

        self.overload_alarm = ft.Switch(
            label="Overload Alarm", label_position=ft.LabelPosition.LEFT, col={"md": 6},
            value=self.last_propeller_setting.alarm_enabled_of_overload_curve,
            on_change=lambda e: setattr(self.last_propeller_setting, 'alarm_enabled_of_overload_curve', e.control.value)
        )

        self.line_color_of_overload_curve = ColorDialog(
            on_change=lambda color: setattr(self.last_propeller_setting,'line_color_of_overload_curve', color)
        )
        self.line_color_of_overload_curve.set_color(self.last_propeller_setting.line_color_of_overload_curve)

        self.overload_curve_card = create_card(
            'Overload Curve (5)',
            ft.Column(
                controls=[
                    self.overload_curve,
                    self.overload_alarm,
                    self.line_color_of_overload_curve.create()
                ]
            ),
            col={"md": 6})

    def __save_data(self,e):
        self.last_propeller_setting.save()
        Toast.show_success(e.page, message="保存成功")

    def __cancel_data(self,e):
        self.last_propeller_setting = PropellerSetting.select().order_by(PropellerSetting.id.desc()).first()

        self.rpm_of_mcr_operating_point.value = self.last_propeller_setting.rpm_of_mcr_operating_point
        self.shaft_power_of_mcr_operating_point.value = self.last_propeller_setting.shaft_power_of_mcr_operating_point
        self.mcr_operating_point_card.update()

        self.rpm_left_of_normal_propeller_curve.value = self.last_propeller_setting.rpm_left_of_normal_propeller_curve
        self.bhp_left_of_normal_propeller_curve.value = self.last_propeller_setting.bhp_left_of_normal_propeller_curve
        self.rpm_right_of_normal_propeller_curve.value = self.last_propeller_setting.rpm_right_of_normal_propeller_curve
        self.bhp_right_of_normal_propeller_curve.value = self.last_propeller_setting.bhp_right_of_normal_propeller_curve
        self.line_color_of_normal_propeller_curve.set_color(self.last_propeller_setting.line_color_of_normal_propeller_curve)
        self.normal_propeller_curve_card.update()

        self.rpm_left_of_torque_load_limit_curve.value = self.last_propeller_setting.rpm_left_of_torque_load_limit_curve
        self.bhp_left_of_torque_load_limit_curve.value = self.last_propeller_setting.bhp_left_of_torque_load_limit_curve
        self.rpm_right_of_torque_load_limit_curve.value = self.last_propeller_setting.rpm_right_of_torque_load_limit_curve
        self.bhp_right_of_torque_load_limit_curve.value = self.last_propeller_setting.bhp_right_of_torque_load_limit_curve
        self.line_color_of_torque_load_limit_curve.set_color(self.last_propeller_setting.line_color_of_torque_load_limit_curve)
        self.torque_load_limit_curve_card.update()

        self.light_propeller_curve.value = self.last_propeller_setting.value_of_light_propeller_curve
        self.line_color_of_light_propeller_curve.set_color(self.last_propeller_setting.line_color_of_light_propeller_curve)
        self.light_propeller_curve_card.update()

        self.speed_limit_curve.value = self.last_propeller_setting.value_of_speed_limit_curve
        self.line_color_of_speed_limit_curve.set_color(self.last_propeller_setting.line_color_of_speed_limit_curve)
        self.speed_limit_curve_card.update()

        self.overload_curve.value = self.last_propeller_setting.value_of_overload_curve
        self.line_color_of_overload_curve.set_color(self.last_propeller_setting.line_color_of_overload_curve)
        self.overload_alarm.value = self.last_propeller_setting.alarm_enabled_of_overload_curve
        self.overload_curve_card.update()
        Toast.show_success(e.page, message="已取消")

    def create(self):
        self.__create_mcr_operating_point(),
        self.__create_normal_propeller_curve(),
        self.__create_torque_load_limit_curve(),
        self.__create_light_propeller_curve(),
        self.__create_speed_limit_curve(),
        self.__create_overload_curve(),
        return ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            # 这里有bug，如果添加了，外部页面就会居中
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                ft.ResponsiveRow(
                    expand=True,
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
                                ft.FilledButton(
                                                text="Save",
                                                width=120,
                                                height=40,
                                                on_click=lambda e:self.__save_data(e)),

                                ft.OutlinedButton(
                                                text="Cancel",
                                                width=120,
                                                height=40,
                                                on_click=lambda e:self.__cancel_data(e))
                            ])
                    ])])
