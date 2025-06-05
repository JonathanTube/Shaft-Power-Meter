import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
import serial.tools.list_ports
from utils.modbus_output import modbus_output


class IOSettingOutput(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        options = [
            ft.dropdown.Option(key=port.name, text=f"{port.name} - {port.description}")
            for port in serial.tools.list_ports.comports()
        ]

        self.serial_port = ft.Dropdown(
            expand=True,
            label="Port",
            width=800,
            value=self.conf.output_com_port,
            options=options
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

        self.heading = self.page.session.get("lang.setting.output_conf")
        self.body = ft.Column(
            controls=[
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
                self.serial_port
            ]
        )
        self.col = {"sm": 12}
        super().build()

    def save_data(self):
        self.conf.output_torque = self.check_torque.value
        self.conf.output_thrust = self.check_thrust.value
        self.conf.output_power = self.check_power.value
        self.conf.output_speed = self.check_speed.value
        self.conf.output_avg_power = self.check_avg_power.value
        self.conf.output_sum_power = self.check_sum_power.value
        self.conf.output_com_port = self.serial_port.value
        count_list = [
            self.conf.output_torque,
            self.conf.output_thrust,
            self.conf.output_power,
            self.conf.output_speed,
            self.conf.output_avg_power,
            self.conf.output_sum_power
        ]
        output_count: int = sum(count_list)
        if output_count > 0:
            self.page.run_task(self.__start_modbus_server)

    async def __start_modbus_server(self):
        await modbus_output.stop_modbus_server()
        await modbus_output.start_modbus_server()
