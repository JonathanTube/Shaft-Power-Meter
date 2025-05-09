import flet as ft

from utils.unit_parser import UnitParser


class CounterDisplay(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.symmetric(horizontal=20, vertical=20)

    def __create_label(self, text: str = ""):
        return ft.Text(
            value=f"{text}:",
            text_align=ft.TextAlign.RIGHT
        )

    def __create_value(self):
        return ft.Text(value="0", size=14, weight=ft.FontWeight.BOLD)

    def __create_unit(self, text: str):
        return ft.Text(
            value=text,
            width=30
        )

    def __create_total_energy(self):
        self.total_energy_value = self.__create_value()
        self.total_energy_label = self.__create_label(
            self.page.session.get('lang.counter.total_energy')
        )
        self.total_energy_unit = self.__create_unit('kWh')

        self.total_energy = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.ENERGY_SAVINGS_LEAF_OUTLINED, size=16),
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

    def __create_average_power(self):
        self.average_power_label = self.__create_label(
            self.page.session.get('lang.counter.average_power')
        )
        self.average_power_value = self.__create_value()
        self.average_power_unit = self.__create_unit('W')

        self.average_power = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.ELECTRIC_BOLT_OUTLINED, size=16),
                        self.average_power_label
                    ]
                ),
                ft.Row(controls=[
                    self.average_power_value,
                    self.average_power_unit]
                )
            ]
        )

    def __create_average_speed(self):
        self.average_speed_label = self.__create_label(self.page.session.get('lang.counter.average_speed'))
        self.average_speed_value = self.__create_value()
        self.average_speed_unit = self.__create_unit('rpm')

        self.average_speed = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.SPEED_OUTLINED, size=16),
                        self.average_speed_label
                    ]
                ),
                ft.Row(controls=[
                    self.average_speed_value,
                    self.average_speed_unit
                ])
            ]
        )

    def build(self):
        self.__create_total_energy()
        self.__create_average_power()
        self.__create_average_speed()
        self.content = ft.Column(
            expand=True,
            controls=[
                self.total_energy,
                self.average_power,
                self.average_speed
            ]
        )

    def set_total_energy(self, total_energy: float, system_unit: int):
        value_and_unit = UnitParser.parse_energy(total_energy, system_unit)
        self.total_energy_value.value = value_and_unit[0]
        self.total_energy_unit.value = value_and_unit[1]
        self.total_energy.update()

    def set_average_power(self, average_power: float, system_unit: int):
        value_and_unit = UnitParser.parse_power(average_power, system_unit)
        self.average_power_value.value = value_and_unit[0]
        self.average_power_unit.value = value_and_unit[1]
        self.average_power.update()

    def set_average_speed(self, average_speed: int):
        value_and_unit = UnitParser.parse_speed(average_speed)
        self.average_speed_value.value = value_and_unit[0]
        self.average_speed_unit.value = value_and_unit[1]
        self.average_speed.update()
