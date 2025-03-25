import flet as ft
import asyncio
from db.models.data_log import DataLog
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser
from db.models.limitations import Limitations
from db.models.system_settings import SystemSettings


class DualPowerSpeedTorque(ft.Container):
    def __init__(self, name: str = 'SPS1'):
        super().__init__()
        self.name = name

        self.speed_max = 0
        self.speed_warning = 0
        self.power_max = 0
        self.power_warning = 0
        self.torque_max = 0
        self.torque_warning = 0

        self.display_thrust = False

        self.padding = ft.padding.only(
            left=10, right=10, top=10, bottom=10
        )
        self.border_radius = ft.border_radius.all(10)
        self.shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=4,
            color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE),
            offset=ft.Offset(0, 1),
            blur_style=ft.ShadowBlurStyle.OUTER
        )

        self.__load_settings()

    def did_mount(self):
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def __load_settings(self):
        limitations = Limitations.get_or_none()

        if limitations:
            self.speed_max = limitations.speed_max
            self.speed_warning = limitations.speed_warning

            self.power_max = limitations.power_max
            self.power_warning = limitations.power_warning

            self.torque_max = limitations.torque_max
            self.torque_warning = limitations.torque_warning

        system_settings = SystemSettings.get_or_none()
        if system_settings:
            self.display_thrust = system_settings.display_thrust

    async def __load_data(self):
        while True:
            data_log = DataLog.select(
                DataLog.revolution,
                DataLog.power,
                DataLog.torque,
                DataLog.thrust
            ).where(
                DataLog.name == self.name
            ).order_by(DataLog.id.desc()).first()
            if data_log:
                speed_and_unit = UnitParser.parse_speed(data_log.revolution)
                speed_value = speed_and_unit[0]
                speed_unit = speed_and_unit[1]
                self.speed_meter.set_data(
                    speed_value,
                    speed_unit,
                    self.speed_max,
                    self.speed_warning
                )

                power_and_unit = UnitParser.parse_power(data_log.power)
                power_value = power_and_unit[0]
                power_unit = power_and_unit[1]
                self.power_meter.set_data(
                    power_value, power_unit,
                    self.power_max, self.power_warning
                )

                torque_and_unit = UnitParser.parse_torque(data_log.torque)
                torque_value = torque_and_unit[0]
                torque_unit = torque_and_unit[1]
                self.torque_meter.set_data(
                    torque_value, torque_unit,
                    self.torque_max, self.torque_warning
                )

                thrust_and_unit = UnitParser.parse_thrust(data_log.thrust)
                self.thrust_value.value = thrust_and_unit[0]
                self.thrust_unit.value = thrust_and_unit[1]
                self.thrust_power.update()

            await asyncio.sleep(1)

    def __create_thrust_power(self):
        self.thrust_value = ft.Text("0")
        self.thrust_unit = ft.Text("W")
        self.thrust_power = ft.Column(
            expand=True,
            right=0,
            top=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Thrust Power", weight=ft.FontWeight.W_500),
                ft.Row(controls=[self.thrust_value, self.thrust_unit])
            ],
            visible=self.display_thrust
        )

    def build(self):
        width = self.page.window.width * 0.45
        height = self.page.window.height * 0.4
        self.speed_meter = MeterRound(
            heading="Speed",
            radius=80,
            unit="rpm",
            border=False,
            color="#7851A9"
        )
        self.power_meter = MeterRound(
            heading="Power",
            radius=100,
            unit="W",
            border=False,
            color="#FF6B35"
        )
        self.torque_meter = MeterRound(
            heading="Torque",
            radius=80,
            unit="Nm",
            border=False,
            color="#A7E647"
        )
        self.__create_thrust_power()

        self.content = ft.Stack(
            width=width,
            height=height,
            alignment=ft.alignment.center,
            controls=[
                ft.Text(
                    value=self.name,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    left=0,
                    top=0
                ),
                ft.Container(
                    content=self.speed_meter,
                    bottom=0,
                    left=0
                ),
                ft.Container(
                    content=self.power_meter
                ),
                ft.Container(
                    content=self.torque_meter,
                    bottom=0,
                    right=0
                ),
                self.thrust_power
            ])
