import flet as ft

from src.ui.common.Meter import Meter
from src.ui.common.custom_card import create_card
from src.ui.home.dashboard.power_line_chart import createPowerLineChart


class DashboardShaPoLiOn:

    def __create_left(self):
        col = ft.Column(
            spacing=40,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text('EEXI Limited Power(%)', weight=ft.FontWeight.BOLD, size=20),
                Meter(radius=160).create()
            ])

        container = ft.Container(expand=True, padding=ft.padding.symmetric(30, 40), content=col)

        self.left = ft.Card(expand=True, content=container)

    def __create_right(self):
        self.right = ft.GridView(
            expand=True,  # 填满父容器
            child_aspect_ratio=1,  # 子项宽高比
            # max_extent=400,  # 子项最大宽度
            runs_count=2,  # 每行分割为2份
            spacing=10,  # 子项间距
            run_spacing=10,  # 行间距
            controls=[
                create_card(heading="Power", body=ft.Text('9999 kw')),
                create_card(heading="Speed", body=ft.Text('9999 rpm')),
                create_card(heading="Torque", body=ft.Text('9999 kNm')),
                create_card(heading="Thrust", body=ft.Text('9999 kN'))
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
                createPowerLineChart()
            ])
