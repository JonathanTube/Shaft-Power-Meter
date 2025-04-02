import flet as ft

from utils.unit_parser import UnitParser


class CounterDisplay(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        # self.bgcolor = "yellow"

    def __create_label(self, text: str = ""):
        return ft.Text(
            value=f"{text}:",
            size=14,
            text_align=ft.TextAlign.RIGHT,
            width=180
        )

    def __create_value(self):
        return ft.Text(value="", size=14, weight=ft.FontWeight.BOLD)

    def __create_unit(self, text: str):
        return ft.Text(
            value=text,
            size=12,
            width=40
        )

    def __create_sum_power(self):
        self.sum_power_value = self.__create_value()
        self.sum_power_label = self.__create_label('Sum Power')
        self.sum_power_unit = self.__create_unit('kWh')

        self.sum_power = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.sum_power_label,
                ft.Row(
                    controls=[
                        self.sum_power_value,
                        self.sum_power_unit
                    ])
            ]
        )

    def __create_average_power(self):
        self.average_power_label = self.__create_label('Average Power')
        self.average_power_value = self.__create_value()
        self.average_power_unit = self.__create_unit('kWh')

        self.average_power = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.average_power_label,
                ft.Row(controls=[
                    self.average_power_value,
                    self.average_power_unit]
                )
            ]
        )

    def __create_number_of_revolutions(self):
        self.number_of_revolutions_label = self.__create_label(
            'Number of Revolutions')
        self.number_of_revolutions_value = self.__create_value()

        self.number_of_revolutions = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.number_of_revolutions_label,
                ft.Row(controls=[self.number_of_revolutions_value]),
                ft.Text("")
            ]
        )

    def __create_average_speed(self):
        self.average_speed_label = self.__create_label('Average Speed')
        self.average_speed_value = self.__create_value()
        self.average_speed_unit = self.__create_unit('rpm')

        self.average_speed = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.average_speed_label,
                ft.Row(controls=[
                    self.average_speed_value,
                    self.average_speed_unit
                ])
            ]
        )

    def build(self):
        self.__create_sum_power(),
        self.__create_average_power(),
        self.__create_number_of_revolutions(),
        self.__create_average_speed()
        self.content = ft.Column(
            expand=True,
            controls=[
                self.sum_power,
                self.average_power,
                self.number_of_revolutions,
                self.average_speed
            ]
        )

    def set_sum_power(self, sum_power: float, system_unit: int):
        value_and_unit = UnitParser.parse_energy(sum_power, system_unit)
        self.sum_power_value.value = value_and_unit[0]
        self.sum_power_unit.value = value_and_unit[1]
        self.sum_power.update()

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

    def set_number_of_revolutions(self, number_of_revolutions: int):
        self.number_of_revolutions_value.value = number_of_revolutions
        self.number_of_revolutions.update()
