import flet as ft


class CounterDisplay(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def __create_label(self, text: str = ""):
        return ft.Text(
            value=text,
            size=14,
            text_align=ft.TextAlign.RIGHT,
            width=140
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
        self.sum_power_label = self.__create_label('Sum Power')
        self.sum_power_value = self.__create_value()
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

    def __create_speed(self):
        self.speed_label = self.__create_label('Speed')
        self.speed_value = self.__create_value()

        self.speed = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self.speed_label,
                ft.Row(controls=[self.speed_value])
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
        self.content = ft.Column(
            expand=True,
            controls=[
                self.__create_sum_power(),
                # self.__create_average_power(),
                # self.__create_speed(),
                # self.__create_average_speed()
            ]
        )

    def set_data(self, sum_power: float, average_power: float, speed: int, average_speed: int):
        self.sum_power_value.value = sum_power
        self.average_power_value.value = average_power
        self.speed_value.value = speed
        self.average_speed_value.value = average_speed
