import logging
import flet as ft
import serial.tools.list_ports
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast
from task.modbus_output_task import modbus_output
from common.global_data import gdata


class IOSettingOutput(ft.Container):
    def build(self):
        try:
            if self.page and self.page.session:
                options = [
                    ft.dropdown.Option(key=port.name, text=f"{port.name} - {port.description}")
                    for port in serial.tools.list_ports.comports()
                ]

                self.serial_port = ft.Dropdown(
                    label="Port",
                    value=gdata.configIO.output_com_port,
                    col={'sm': 8},
                    options=options
                )

                self.start_btn = ft.FilledButton(
                    text=self.page.session.get('lang.setting.connect'),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    visible=False,
                    col={'sm': 4},
                    on_click=lambda e: self.on_start()
                )

                self.stop_btn = ft.FilledButton(
                    text=self.page.session.get('lang.setting.disconnect'),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    visible=False,
                    col={'sm': 4},
                    on_click=lambda e: self.on_stop()
                )

                self.check_torque = ft.Checkbox(
                    label=self.page.session.get("lang.common.torque"),
                    value=gdata.configIO.output_torque
                )
                self.check_thrust = ft.Checkbox(
                    label=self.page.session.get("lang.common.thrust"),
                    value=gdata.configIO.output_thrust
                )

                self.check_power = ft.Checkbox(
                    label=self.page.session.get("lang.common.power"),
                    value=gdata.configIO.output_power
                )

                self.check_speed = ft.Checkbox(
                    label=self.page.session.get("lang.common.speed"),
                    value=gdata.configIO.output_speed
                )

                self.check_avg_power = ft.Checkbox(
                    label=self.page.session.get("lang.common.average_power"),
                    value=gdata.configIO.output_avg_power
                )

                self.check_total_energy = ft.Checkbox(
                    label=self.page.session.get("lang.common.total_energy"),
                    value=gdata.configIO.output_total_energy
                )

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.output_conf"),
                    ft.Column(controls=[
                        ft.Row(
                            expand=True,
                            controls=[
                                self.check_torque,
                                self.check_thrust,
                                self.check_speed,
                                self.check_power,
                                self.check_avg_power,
                                self.check_total_energy
                            ]
                        ),
                        ft.Row(
                            expand=True,
                            alignment=ft.alignment.center,
                            controls=[
                                self.serial_port,
                                self.start_btn,
                                self.stop_btn
                            ]
                        )
                    ]))
                self.content = self.custom_card
        except:
            logging.exception('exception occured at IOSettingOutput.build')

    def on_start(self):
        try:
            self.save_data()
            gdata.configIO.set_default_value()

            if self.start_btn and self.start_btn.page:
                self.start_btn.text = "loading..."
                self.start_btn.bgcolor = ft.Colors.GREY
                self.start_btn.disabled = True
                self.start_btn.update()

            count_list = [
                gdata.configIO.output_torque,
                gdata.configIO.output_thrust,
                gdata.configIO.output_power,
                gdata.configIO.output_speed,
                gdata.configIO.output_avg_power,
                gdata.configIO.output_total_energy
            ]
            output_count: int = sum(count_list)
            if output_count == 0:
                Toast.show_warning(self.page, self.page.session.get('lang.setting.io_conf.output_option_does_not_selected'))
                return

            if self.serial_port.value is None:
                Toast.show_warning(self.page, self.page.session.get('lang.setting.io_conf.serial_port_can_not_be_empty'))
                return

            self.page.run_task(modbus_output.start)
        except Exception as e:
            Toast.show_error(self.page, str(e))

    def on_stop(self):
        try:
            if self.stop_btn and self.stop_btn.page:
                self.stop_btn.text = "loading..."
                self.stop_btn.bgcolor = ft.Colors.GREY
                self.stop_btn.disabled = True
                self.stop_btn.update()

            self.page.run_task(modbus_output.stop)
        except:
            logging.exception('exception occured at IOSettingOutput.on_start')

    def save_data(self):
        output_torque = bool(self.check_torque.value)
        output_thrust = bool(self.check_thrust.value)
        output_power = bool(self.check_power.value)
        output_speed = bool(self.check_speed.value)
        output_avg_power = bool(self.check_avg_power.value)
        output_total_energy = bool(self.check_total_energy.value)
        output_com_port = self.serial_port.value  # 保存串口名
        IOConf.update(
            output_torque=output_torque, output_thrust=output_thrust,
            output_power=output_power, output_speed=output_speed,
            output_avg_power=output_avg_power, output_total_energy=output_total_energy,
            output_com_port=output_com_port
        ).execute()

    def before_update(self):
        try:
            if self.page and self.page.session:
                if self.start_btn:
                    self.start_btn.visible = not modbus_output.is_started
                    self.start_btn.text = self.page.session.get("lang.setting.connect")
                    self.start_btn.bgcolor = ft.Colors.GREEN
                    self.start_btn.disabled = False

                if self.stop_btn:
                    self.stop_btn.visible = modbus_output.is_started
                    self.stop_btn.text = self.page.session.get("lang.setting.disconnect")
                    self.stop_btn.bgcolor = ft.Colors.RED
                    self.stop_btn.disabled = False
        except:
            logging.exception('exception occured at IOSettingOutput.before_update')
