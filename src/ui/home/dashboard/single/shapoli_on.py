import flet as ft

from ..power_chart import PowerChart
from ....common.meter_half import MeterHalf
from ....common.custom_card import create_card


class DashboardShaPoLiOn:

    def __create_left(self):
        column = ft.Column(
            expand=True,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text('EEXI Limited Power(%)', weight=ft.FontWeight.BOLD, size=20),
                MeterHalf(radius=150).create()
            ])

        container = ft.Container(expand=True, padding=ft.padding.symmetric(10, 10), content=column)

        self.left = ft.Card(content=container)

    @staticmethod
    def __create_small_card(heading: str, controls: list[ft.Control]):
        return ft.Card(
            expand=True,
            content=ft.Stack(
                controls=[
                    ft.Text(heading, weight=ft.FontWeight.W_600, size=16, left=10, top=10),
                    ft.Row(controls=controls, right=10, bottom=30)
                ]
            ))

    def __create_right(self):
        self.power_text = ft.Text('9999', size=24, weight=ft.FontWeight.W_500)
        self.speed_text = ft.Text('8888', size=24, weight=ft.FontWeight.W_500)
        self.torque_text = ft.Text('7777', size=24, weight=ft.FontWeight.W_500)
        self.thrust_text = ft.Text('6666', size=24, weight=ft.FontWeight.W_500)

        content = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=True,
                    controls=[
                        self.__create_small_card(
                            heading="Power",
                            controls=[self.power_text, ft.Text('kw', size=18)]
                        ),
                        self.__create_small_card(
                            heading="Speed",
                            controls=[self.speed_text, ft.Text('rpm', size=18)]
                        )
                    ]),
                ft.Row(
                    expand=True,
                    controls=[
                        self.__create_small_card(
                            heading="Torque",
                            controls=[self.torque_text, ft.Text('kNm', size=18)]
                        ),
                        self.__create_small_card(
                            heading="Thrust",
                            controls=[self.thrust_text, ft.Text('kN', size=18)]
                        )
                    ])
            ]
        )

        self.right = ft.Container(expand=False, width=350, height=300, content=content)

    def __create_top_right(self):
        self.unlimited_power_text = ft.Text('5555', weight=ft.FontWeight.W_600)
        self.limited_power_text = ft.Text('4444', weight=ft.FontWeight.W_600)

        unlimited_power = ft.Row(
            controls=[
                ft.Text("Unlimited Power:", width=120, text_align=ft.TextAlign.RIGHT),
                self.unlimited_power_text,
                ft.Text('kw')
            ]
        )
        limited_power = ft.Row(
            controls=[
                ft.Text("Limited Power:", width=120, text_align=ft.TextAlign.RIGHT),
                self.limited_power_text,
                ft.Text('kw')
            ]
        )

        self.top_right = ft.Container(
            expand=False,
            top=10,
            right=10,
            border_radius=ft.BorderRadius(5, 5, 5, 5),
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            content=ft.Stack(controls=[
                ft.Container(content=ft.Icon(name=ft.Icons.LIGHTBULB_OUTLINE), left=0, top=2),
                ft.Container(content=ft.Column(controls=[unlimited_power, limited_power]), margin=15)
            ]))

    def __create_summary(self):
        self.__create_left()
        self.__create_right()
        empty_placeholder = ft.Container(width=150, height=100)
        self.summary = ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[self.left, self.right, empty_placeholder]
        )

    def create(self):
        self.__create_summary()
        self.__create_top_right()

        main = ft.Column(
            expand=True,
            controls=[
                self.summary,
                create_card(heading="Power", body=PowerChart().create())
            ])

        return ft.Stack(
            controls=[
                ft.Container(content=main, margin=ft.Margin(left=0, top=20, right=0, bottom=0)),
                self.top_right
            ]
        )
