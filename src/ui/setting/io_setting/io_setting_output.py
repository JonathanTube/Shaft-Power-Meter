import logging
import flet as ft
import serial.tools.list_ports
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast
from utils.modbus_output import modbus_output
from common.global_data import gdata


class IOSettingOutput(ft.Container):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        try:
            options = [
                ft.dropdown.Option(key=port.name, text=f"{port.name} - {port.description}")
                for port in serial.tools.list_ports.comports()
            ]

            self.serial_port = ft.Dropdown(
                label="Port",
                value=self.conf.output_com_port,
                options=options
            )

            self.connect_button = ft.FilledButton(
                text=self.page.session.get('lang.setting.connect'),
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                visible=not gdata.modbus_server_started,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                on_click=lambda e: self.__on_connect(e)
            )

            self.disconnect_button = ft.FilledButton(
                text=self.page.session.get('lang.setting.disconnect'),
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                visible=gdata.modbus_server_started,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                on_click=lambda e: self.__on_disconnect(e)
            )

            self.check_torque = ft.Checkbox(
                label=self.page.session.get("lang.common.torque"),
                value=self.conf.output_torque
            )
            self.check_thrust = ft.Checkbox(
                label=self.page.session.get("lang.common.thrust"),
                value=self.conf.output_thrust
            )

            self.check_power = ft.Checkbox(
                label=self.page.session.get("lang.common.power"),
                value=self.conf.output_power
            )

            self.check_speed = ft.Checkbox(
                label=self.page.session.get("lang.common.speed"),
                value=self.conf.output_speed
            )

            self.check_avg_power = ft.Checkbox(
                label=self.page.session.get("lang.common.average_power"),
                value=self.conf.output_avg_power
            )

            self.check_sum_power = ft.Checkbox(
                label=self.page.session.get("lang.common.total_energy"),
                value=self.conf.output_sum_power
            )

            self.custom_card = CustomCard(
                self.page.session.get("lang.setting.output_conf"),
                ft.ResponsiveRow(controls=[
                    ft.Row(
                        expand=True,
                        controls=[
                            self.check_torque,
                            self.check_thrust,
                            self.check_speed,
                            self.check_power,
                            self.check_avg_power,
                            self.check_sum_power
                        ]),
                    ft.Row(
                        expand=True,
                        controls=[
                            self.serial_port,
                            self.connect_button,
                            self.disconnect_button
                        ]
                    )
                ]))
            self.content = self.custom_card
        except:
            logging.exception('exception occured at IOSettingOutput.build')

    def __on_connect(self, e):
        self.save_data()
        self.conf.save()
        count_list = [
            self.conf.output_torque,
            self.conf.output_thrust,
            self.conf.output_power,
            self.conf.output_speed,
            self.conf.output_avg_power,
            self.conf.output_sum_power
        ]
        output_count: int = sum(count_list)
        if output_count == 0:
            Toast.show_warning(self.page, self.page.session.get('lang.setting.io_conf.output_option_does_not_selected'))
            return
        if self.serial_port.value is None:
            Toast.show_warning(self.page, self.page.session.get('lang.setting.io_conf.serial_port_can_not_be_empty'))
            return

        self.page.run_task(self.__end_modbus_server)
        self.page.run_task(self.__start_modbus_server)

    def __on_disconnect(self, e):
        self.page.run_task(self.__end_modbus_server)

    def save_data(self):
        self.conf.output_torque = self.check_torque.value
        self.conf.output_thrust = self.check_thrust.value
        self.conf.output_power = self.check_power.value
        self.conf.output_speed = self.check_speed.value
        self.conf.output_avg_power = self.check_avg_power.value
        self.conf.output_sum_power = self.check_sum_power.value
        self.conf.output_com_port = self.serial_port.value

    async def __start_modbus_server(self):
        try:
            succ = await modbus_output.start()
            self.connect_button.visible = not succ
            self.connect_button.update()
            self.disconnect_button.visible = succ
            self.disconnect_button.update()
        except Exception as e:
            logging.exception(e)

    async def __end_modbus_server(self):
        try:
            succ = await modbus_output.stop_modbus_server()
            self.connect_button.visible = succ
            self.connect_button.update()
            self.disconnect_button.visible = not succ
            self.disconnect_button.update()
        except Exception as e:
            logging.exception(e)
