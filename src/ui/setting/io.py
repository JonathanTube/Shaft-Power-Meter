import flet as ft

from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast


class IO(ft.Container):
    def __init__(self):
        super().__init__()
        self.last_io_conf = IOConf.get()

    def __create_plc_conf(self):
        self.plc_ip = ft.TextField(
            label="IP Address", value=self.last_io_conf.plc_ip, col={'md': 6},
            on_change=lambda e: setattr(
                self.last_io_conf, 'plc_ip', e.control.value)
        )

        self.plc_port = ft.TextField(
            label="Port", value=self.last_io_conf.plc_port, col={'md': 6},
            on_change=lambda e: setattr(
                self.last_io_conf, 'plc_port', e.control.value)
        )

        self.plc_conf = CustomCard(
            'PLC Conf.',
            body=ft.ResponsiveRow(controls=[
                self.plc_ip,
                self.plc_port
            ]),
            col={"md": 12}
        )

    def __create_output_conf(self):
        self.check_torque = ft.Checkbox(
            label="Torque(kNm)",
            value=self.last_io_conf.output_torque,
            on_change=lambda e: setattr(self.last_io_conf, 'output_torque', e.control.value))

        self.check_thrust = ft.Checkbox(
            label="Thrust(kN)",
            value=self.last_io_conf.output_thrust,
            on_change=lambda e: setattr(self.last_io_conf, 'output_thrust', e.control.value))

        self.check_power = ft.Checkbox(
            label="Power(kw)",
            value=self.last_io_conf.output_power,
            on_change=lambda e: setattr(self.last_io_conf, 'output_power', e.control.value))

        self.check_speed = ft.Checkbox(
            label="Speed(rpm)",
            value=self.last_io_conf.output_speed,
            on_change=lambda e: setattr(self.last_io_conf, 'output_speed', e.control.value))

        self.check_avg_power = ft.Checkbox(
            label="Average Power(kw)",
            value=self.last_io_conf.output_avg_power,
            on_change=lambda e: setattr(self.last_io_conf, 'output_avg_power', e.control.value))

        self.check_sum_power = ft.Checkbox(
            label="Sum Of Power(kwh)",
            value=self.last_io_conf.output_sum_power,
            on_change=lambda e: setattr(self.last_io_conf, 'output_sum_power', e.control.value))

        self.output_conf = CustomCard(
            'Output Conf.',
            body=ft.ResponsiveRow(controls=[
                self.check_torque,
                self.check_thrust,
                self.check_power,
                self.check_speed,
                self.check_avg_power,
                self.check_sum_power
            ]),
            col={"md": 12}
        )

    def __save_data(self, e):
        self.last_io_conf.save()
        Toast.show_success(e.page)

    def __cancel_data(self, e):
        self.__load_data()

        self.plc_ip.value = self.last_io_conf.plc_ip
        self.plc_ip.update()

        self.plc_port.value = self.last_io_conf.plc_port
        self.plc_port.update()

        Toast.show_success(e.page)

    def build(self):
        self.__create_plc_conf()
        self.__create_output_conf()

        self.save_button = ft.FilledButton(
            text="Save", width=120, height=40, on_click=self.__save_data)
        self.cancel_button = ft.OutlinedButton(
            text="Cancel", width=120, height=40, on_click=self.__cancel_data)

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.ResponsiveRow(
                    controls=[
                        self.plc_conf,
                        self.output_conf,
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
        )

    def __set_language(self):
        session = self.page.session
        self.plc_conf.set_title(session.get("lang.setting.plc_conf"))
        self.plc_ip.label = session.get("lang.setting.plc_ip")
        self.plc_port.label = session.get("lang.setting.plc_port")

        self.output_conf.set_title(session.get("lang.setting.output_conf"))
        self.check_torque.label = session.get("lang.common.torque")
        self.check_thrust.label = session.get("lang.common.thrust")
        self.check_power.label = session.get("lang.common.power")
        self.check_speed.label = session.get("lang.common.speed")
        self.check_avg_power.label = session.get("lang.common.average_power")
        self.check_sum_power.label = session.get("lang.common.sum_power")

        self.save_button.text = session.get("lang.button.save")
        self.cancel_button.text = session.get("lang.button.cancel")

    def before_update(self):
        self.__set_language()

    def did_mount(self):
        self.__set_language()
