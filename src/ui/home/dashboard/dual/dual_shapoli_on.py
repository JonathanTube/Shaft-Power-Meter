import flet as ft

from ui.common.meter_half import MeterHalf


class DualShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()
        self.font_size_of_label = 14
        self.font_size_of_value = 16
        self.font_size_of_unit = 12

        self.content = self.__create()
        self.expand = True

    def __create_left(self):
        column = ft.Column(
            expand=False,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text('EEXI Limited Power(%)',
                        weight=ft.FontWeight.BOLD, size=20),
                MeterHalf(radius=200)
            ])

        container = ft.Container(
            expand=False, padding=ft.padding.symmetric(10, 10), content=column)

        self.left = ft.Card(expand=False, content=container)

    @staticmethod
    def __create_small_card(heading: str, controls: list[ft.Control]):
        header = ft.Text(
            heading,
            weight=ft.FontWeight.W_600,
            size=16, left=10, top=10
        )
        content = ft.Column(
            controls=controls,
            spacing=4,
            right=10,
            bottom=10
        )
        return ft.Card(expand=True,
                       content=ft.Stack(controls=[header, content]))

    def __create_power(self):
        self.power_sps1_value = ft.Text(
            '9999', size=self.font_size_of_value, weight=ft.FontWeight.W_500)
        self.power_sps2_value = ft.Text(
            '9999', size=self.font_size_of_value, weight=ft.FontWeight.W_500)
        self.power_total_value = ft.Text(
            '9999', size=self.font_size_of_value, weight=ft.FontWeight.W_500)

        self.power_sps1 = ft.Row(controls=[
            ft.Text('SPS1:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600),
            self.power_sps1_value,
            ft.Text('kw', size=self.font_size_of_unit)
        ])
        self.power_sps2 = ft.Row(controls=[
            ft.Text('SPS2:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600),
            self.power_sps2_value,
            ft.Text('kw', size=self.font_size_of_unit)
        ])
        self.power_total = ft.Row(controls=[
            ft.Text('Total',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600),
            self.power_total_value,
            ft.Text('kw', size=self.font_size_of_unit)
        ])

        return self.__create_small_card(
            heading="Power",
            controls=[self.power_sps1, self.power_sps2, self.power_total]
        )

    def __create_speed(self):
        self.speed_sps1_value = ft.Text(
            '8888', size=self.font_size_of_value, weight=ft.FontWeight.W_500)
        self.speed_sps2_value = ft.Text(
            '8888', size=self.font_size_of_value, weight=ft.FontWeight.W_500)

        self.speed_sps1 = ft.Row(controls=[
            ft.Text('SPS1:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600),
            self.speed_sps1_value,
            ft.Text('rpm', size=self.font_size_of_unit)
        ])
        self.speed_sps2 = ft.Row(controls=[
            ft.Text('SPS2:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600),
            self.speed_sps2_value,
            ft.Text('rpm', size=self.font_size_of_unit)
        ])
        return self.__create_small_card(
            heading="Speed",
            controls=[self.speed_sps1, self.speed_sps2]
        )

    def __create_torque(self):
        self.torque_sps1_value = ft.Text(
            '7777', size=self.font_size_of_value, weight=ft.FontWeight.W_500)
        self.torque_sps2_value = ft.Text(
            '7777', size=self.font_size_of_value, weight=ft.FontWeight.W_500)

        self.torque_sps1 = ft.Row(controls=[
            ft.Text('SPS1:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600),
            self.torque_sps1_value,
            ft.Text('kNm', size=self.font_size_of_unit)
        ])
        self.torque_sps2 = ft.Row(controls=[
            ft.Text('SPS2:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600),
            self.torque_sps2_value,
            ft.Text('kNm', size=self.font_size_of_unit)
        ])
        return self.__create_small_card(
            heading="Torque",
            controls=[self.torque_sps1, self.torque_sps2]
        )

    def __create_thrust(self):
        self.thrust_sps1_value = ft.Text(
            '6666', size=self.font_size_of_value, weight=ft.FontWeight.W_500)
        self.thrust_sps2_value = ft.Text(
            '6666', size=self.font_size_of_value, weight=ft.FontWeight.W_500)

        self.thrust_sps1 = ft.Row(controls=[
            ft.Text('SP1:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600),
            self.thrust_sps1_value,
            ft.Text('kN', size=self.font_size_of_unit)
        ])
        self.thrust_sps2 = ft.Row(controls=[
            ft.Text('SP2:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600),
            self.thrust_sps2_value,
            ft.Text('kN', size=self.font_size_of_unit)
        ])
        return self.__create_small_card(
            heading="Thrust",
            controls=[self.thrust_sps1, self.thrust_sps2]
        )

    def __create_right(self):
        content = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=True,
                    controls=[
                        self.__create_power(),
                        self.__create_speed()
                    ]),
                ft.Row(
                    expand=True,
                    controls=[
                        self.__create_torque(),
                        self.__create_thrust()
                    ])
            ]
        )

        self.right = ft.Container(
            expand=False, width=360, height=300, content=content)

    def __create(self):
        self.__create_left()
        self.__create_right()
        # empty_placeholder = ft.Container(width=150, height=100)
        return ft.Row(
            expand=False,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[self.left, self.right]
        )
