import math

import flet as ft

hide_section = 90


class MeterRound:
    def __init__(self, heading: str, radius: int, value: float, max_value: float, limit_value: float, unit: str):
        self.heading = heading
        self.max_value = max_value
        self.limit_value = limit_value
        self.value = value
        self.unit = unit
        self.max_radius = radius
        self.outer_radius = radius * 0.35
        self.outer_center_space_radius = radius - self.outer_radius

    def __create_ring(self):
        green_section = (360 - hide_section) * self.value / self.max_value
        grey_section = (360 - hide_section) - green_section
        self.ring = ft.PieChart(
            sections_space=0,
            sections=[
                ft.PieChartSection(green_section, color=ft.Colors.GREEN, radius=self.outer_radius),
                ft.PieChartSection(grey_section, color=ft.Colors.GREY_200, radius=self.outer_radius),
                ft.PieChartSection(hide_section, color=ft.Colors.SURFACE, radius=self.outer_radius)
            ],
            start_degree_offset=135,
            center_space_radius=self.outer_center_space_radius,
            expand=True
        )

    def __create_center(self):
        container_width = self.outer_center_space_radius * 2
        left = self.max_radius - container_width * 0.5
        top = left
        font_size = self.max_radius * 0.25
        unit_size = self.max_radius * 0.18

        self.center_text = ft.Text(value=str(self.value), size=font_size, color=ft.Colors.INVERSE_SURFACE)

        self.center_unit = ft.Text(value=self.unit, size=unit_size, color=ft.Colors.INVERSE_SURFACE)

        self.center = ft.Container(
            bgcolor=ft.Colors.SURFACE,
            border_radius=container_width,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.center_text,
                    self.center_unit
                ]),
            width=container_width,
            height=container_width,
            left=left,
            top=top
        )

    def create(self):
        # rotate_value = math.pi * self.value / self.max_value
        rotate_value = (math.pi * 3 / 4) + (2 * math.pi * 3 / 4) * (self.limit_value / self.max_value)

        rotating_line = ft.Container(
            width=self.max_radius,
            height=self.max_radius * 0.05,
            left=self.max_radius,
            top=self.max_radius,
            bgcolor=ft.Colors.AMBER,
            border_radius=5,
            rotate=ft.transform.Rotate(rotate_value, alignment=ft.alignment.center_left)
        )

        self.__create_ring()
        self.__create_center()

        stack = ft.Stack(
            controls=[
                self.ring,
                rotating_line,
                self.center
            ],
            width=self.max_radius * 2,
            height=self.max_radius * 2
        )
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(content=ft.Text(self.heading, size=self.max_radius * 0.2),
                             margin=ft.Margin(left=0, right=0, top=0, bottom=self.max_radius * 0.2)),
                stack
            ])


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.add(
        ft.Container(
            content=MeterRound(heading='Speed',
                               radius=120,
                               value=135.0,
                               max_value=270.0,
                               limit_value=250.0,
                               unit='rpm'
                               ).create()
        )
    )


ft.app(main)
