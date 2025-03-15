import flet as ft

from ....common.Meter import Meter
from ....common.custom_card import create_card
from ..power_chart import PowerChart


class DashboardShaPoLiOn:

    def __create_left(self):
        column = ft.Column(
            expand=True,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text('EEXI Limited Power(%)', weight=ft.FontWeight.BOLD, size=20),
                Meter(radius=150).create()
            ])

        container = ft.Container(expand=True, padding=ft.padding.symmetric(10, 10), content=column)

        self.left = ft.Card(content=container)

    def __create_right(self):
        self.right = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=True,
                    controls=[
                        create_card(expand=True, heading="Power",
                                    body=ft.Row(
                                        expand=True,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        run_alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text('9999', size=28, weight=ft.FontWeight.W_600),
                                            ft.Text('kw', size=18)
                                        ])),
                        create_card(expand=True, heading="Speed", body=ft.Text('9999 rpm')),
                        create_card(expand=True, heading="Torque", body=ft.Text('9999 kNm')),
                    ]),
                ft.Row(
                    expand=True,
                    controls=[
                        create_card(expand=True, heading="Thrust", body=ft.Text('9999 kN')),
                        create_card(expand=True, heading="Unlimited Power", body=ft.Text('100 kW')),
                        create_card(expand=True, heading="Limited Power", body=ft.Text('180 kW'))
                    ])
            ]
        )

    def __create_summary(self):
        self.__create_left()
        self.__create_right()
        self.summary = ft.Row(
            expand=True,
            controls=[
                self.left,
                self.right
            ])

    def create(self):
        self.__create_summary()
        return ft.Column(
            expand=True,
            controls=[
                self.summary,
                PowerChart().create()
            ])
