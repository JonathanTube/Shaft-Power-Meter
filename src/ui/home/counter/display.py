import logging
import flet as ft

from utils.unit_parser import UnitParser


class CounterDisplay(ft.Container):
    def __init__(self):
        super().__init__()
        # self.bgcolor = ft.Colors.GREY_100
        self.padding = ft.padding.only(top=10, bottom=10)

    def __create_label(self, text: str = ""):
        return ft.Text(
            value=f"{text}:",
            text_align=ft.TextAlign.RIGHT
        )

    def __create_value(self):
        return ft.Text(value="0", size=14, weight=ft.FontWeight.BOLD)

    def __create_unit(self, text: str = ""):
        return ft.Text(
            value=text,
            width=40
        )

    def __create_total_energy(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.total_energy_value = self.__create_value()
            self.total_energy_label = self.__create_label(self.page.session.get('lang.counter.total_energy'))
            self.total_energy_unit = self.__create_unit('kWh')

            self.total_energy = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ENERGY_SAVINGS_LEAF_OUTLINED, size=16),
                            self.total_energy_label
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            self.total_energy_value,
                            self.total_energy_unit
                        ])
                ]
            )
        except:
            logging.exception('exception occured at CounterDisplay.__create_total_energy')

    def __create_average_power(self):
        try:
            self.average_power_label = self.__create_label(self.page.session.get('lang.counter.average_power'))
            self.average_power_value = self.__create_value()
            self.average_power_unit = self.__create_unit('kW')

            self.average_power = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ELECTRIC_BOLT_OUTLINED, size=16),
                            self.average_power_label
                        ]
                    ),
                    ft.Row(controls=[
                        self.average_power_value,
                        self.average_power_unit]
                    )
                ]
            )
        except:
            logging.exception('exception occured at CounterDisplay.__create_average_power')

    def __create_average_speed(self):
        try:
            self.average_speed_label = self.__create_label(self.page.session.get('lang.counter.average_speed'))
            self.average_speed_value = self.__create_value()
            self.average_speed_unit = self.__create_unit('rpm')

            self.average_speed = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SPEED_OUTLINED, size=16),
                            self.average_speed_label
                        ]
                    ),
                    ft.Row(controls=[
                        self.average_speed_value,
                        self.average_speed_unit
                    ])
                ]
            )
        except:
            logging.exception('exception occured at CounterDisplay.__create_average_speed')

    def build(self):
        try:
            if self.page is None:
                return

            self.__create_total_energy()
            self.__create_average_power()
            self.__create_average_speed()

            self.content = ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    self.total_energy,
                    self.average_power,
                    self.average_speed
                ]
            )
        except:
            logging.exception('exception occured at CounterDisplay.build')

    def set_total_energy(self, total_energy: float = 0, system_unit: int = 0):
        try:
            value_and_unit = UnitParser.parse_energy(total_energy, system_unit)
            if self.total_energy_value is not None:
                self.total_energy_value.value = value_and_unit[0]

            if self.total_energy_unit is not None:
                self.total_energy_unit.value = value_and_unit[1]

            if self.total_energy and self.total_energy.page:
                self.total_energy.update()
        except:
            logging.exception('exception occured at CounterDisplay.set_total_energy')

    def set_average_power(self, average_power: float = 0, system_unit: int = 0):
        try:
            value_and_unit = UnitParser.parse_power(average_power, system_unit)
            if self.average_power_value is not None:
                self.average_power_value.value = value_and_unit[0]

            if self.average_power_unit is not None:
                self.average_power_unit.value = value_and_unit[1]

            if self.average_power and self.average_power.page:
                self.average_power.update()
        except:
            logging.exception('exception occured at CounterDisplay.set_average_power')

    def set_average_speed(self, average_speed: int = 0):
        try:
            value_and_unit = UnitParser.parse_speed(average_speed)
            if self.average_speed_value is not None:
                self.average_speed_value.value = value_and_unit[0]

            if self.average_speed_unit is not None:
                self.average_speed_unit.value = value_and_unit[1]

            if self.average_speed and self.average_speed.page:
                self.average_speed.update()
        except:
            logging.exception('exception occured at CounterDisplay.set_average_speed')
