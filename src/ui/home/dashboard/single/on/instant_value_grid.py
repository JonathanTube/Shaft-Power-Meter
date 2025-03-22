import flet as ft
import asyncio
from db.models.data_log import DataLog
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from utils.unit_parser import UnitParser


class InstantValueGrid(ft.Container):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.width = width
        self.height = height

        self.limited_power_value = 0
        self.unlimited_power_value = 0

        self.__load_config()
        self.__load_unlimited_power()

    def build(self):
        self.__handle_first_row()
        self.__handle_second_row()
        self.__handle_third_row()
        self.__handle_layout()

    def did_mount(self):
        # create 1s interval to load data, use asyncio
        self._task = asyncio.create_task(self.__load_data())

    def unmount(self):
        self._task.cancel()

    def __load_config(self):
        system_settings = SystemSettings.select().order_by(
            SystemSettings.id.desc()).first()
        if system_settings is None:
            return
        self.display_thrust = system_settings.display_thrust
        self.limited_power_value = system_settings.eexi_limited_power

    def __load_unlimited_power(self):
        propeller_settings = PropellerSetting.select().order_by(
            PropellerSetting.id.desc()).first()
        if propeller_settings is None:
            return
        self.unlimited_power_value = propeller_settings.shaft_power_of_mcr_operating_point

    async def __load_data(self):
        while True:
            print("load data")
            data_log = DataLog.select().order_by(DataLog.id.desc()).first()
            if data_log is None:
                return

            power = UnitParser.parse_power(data_log.power)
            self.power_value.value = power[0]
            self.power_value.update()
            self.power_unit.value = power[1]
            self.power_unit.update()

            speed = UnitParser.parse_speed(data_log.revolution)
            self.speed_value.value = speed[0]
            self.speed_value.update()
            self.speed_unit.value = speed[1]
            self.speed_unit.update()

            torque = UnitParser.parse_torque(data_log.torque)
            self.torque_value.value = torque[0]
            self.torque_value.update()
            self.torque_unit.value = torque[1]
            self.torque_unit.update()

            thrust = UnitParser.parse_thrust(data_log.thrust)
            self.thrust_value.value = thrust[0]
            self.thrust_value.update()
            self.thrust_unit.value = thrust[1]
            self.thrust_unit.update()

            await asyncio.sleep(1)

    def __create_small_card(self, heading: str, controls: list[ft.Control]):
        text = ft.Text(heading,
                       weight=ft.FontWeight.W_600,
                       size=20, left=10, top=10)
        content = ft.Row(controls=controls, right=10, bottom=30)

        return ft.Card(
            expand=True,
            margin=0,
            content=ft.Stack(controls=[text, content])
        )

    def __handle_first_row(self):
        unlimited_power = UnitParser.parse_power(self.unlimited_power_value)
        unlimited_power_value = ft.Text(unlimited_power[0])
        unlimited_power_unit = ft.Text(unlimited_power[1])

        limited_power = UnitParser.parse_power(self.limited_power_value)
        limited_power_value = ft.Text(limited_power[0])
        limited_power_unit = ft.Text(limited_power[1])

        self.first_row = ft.Row(
            controls=[
                ft.Card(
                    margin=0,
                    expand=True,
                    color=ft.colors.SURFACE_CONTAINER_HIGHEST,
                    content=ft.Container(padding=10, content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Un-limited Power",
                                    weight=ft.FontWeight.W_600),
                            ft.Row(controls=[
                                unlimited_power_value,
                                unlimited_power_unit
                            ])
                        ]
                    ))
                ),
                ft.Card(
                    margin=0,
                    expand=True,
                    color=ft.colors.SURFACE_CONTAINER_HIGHEST,
                    content=ft.Container(padding=10, content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text('Limited Power',
                                    weight=ft.FontWeight.W_600),
                            ft.Row(controls=[
                                limited_power_value,
                                limited_power_unit
                            ])
                        ]
                    ))
                )
            ])

    def __handle_second_row(self):
        self.power_value = ft.Text('0', size=18)
        self.power_unit = ft.Text('W', size=18)

        power_card = self.__create_small_card(
            heading="Power",
            controls=[self.power_value, self.power_unit]
        )

        controls = [power_card]

        if self.display_thrust:
            self.thrust_value = ft.Text('0', size=18)
            self.thrust_unit = ft.Text('N', size=18)

            thrust_card = self.__create_small_card(
                heading="Thrust",
                controls=[self.thrust_value, self.thrust_unit]
            )
            controls.append(thrust_card)

        self.second_row = ft.Row(expand=True, controls=controls)

    def __handle_third_row(self):
        self.torque_value = ft.Text('0', size=18)
        self.torque_unit = ft.Text('Nm', size=18)

        self.speed_value = ft.Text('0', size=18)
        self.speed_unit = ft.Text('rps', size=18)

        torque_card = self.__create_small_card(
            heading="Torque",
            controls=[self.torque_value, self.torque_unit]
        )

        speed_card = self.__create_small_card(
            heading="Speed",
            controls=[self.speed_value, self.speed_unit]
        )

        self.third_row = ft.Row(
            expand=True,
            controls=[torque_card, speed_card]
        )

    def __handle_layout(self):
        self.content = ft.Column(
            controls=[
                self.first_row,
                self.second_row,
                self.third_row
            ]
        )
