import math

import flet as ft

hide_section = 90


class MeterRound(ft.Container):
    def __init__(self, heading: str, radius: int, unit: str):
        super().__init__()
        self.heading = heading
        self.unit = unit
        self.max_radius = radius
        self.outer_radius = radius * 0.35
        self.outer_center_space_radius = radius - self.outer_radius
        # set outline style
        self.padding = ft.padding.only(
            left=10, right=10, top=10, bottom=10
        )
        self.border_radius = ft.border_radius.all(10)
        self.shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=4,
            color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE),
            offset=ft.Offset(0, 1),
            blur_style=ft.ShadowBlurStyle.OUTER
        )

    def set_data(self, value: int, unit: str, max_value: int, limit_value: int):
        if max_value == 0:
            return

        # update green section
        green_val = (360 - hide_section) * value / max_value
        self.green_section.value = green_val
        self.green_section.update()

        # update grey section
        grey_val = (360 - hide_section) - green_val
        self.grey_section.value = grey_val
        self.grey_section.update()

        # update center text
        self.center_text.value = value
        self.center_text.update()

        # update unit
        self.center_unit.value = unit
        self.center_unit.update()

        # update warning line
        rotate_start = math.pi * 3 / 4
        rotate_propotion = limit_value / max_value
        rotate_angle = rotate_start + (2 * rotate_start) * rotate_propotion
        self.warning_line_rotate.angle = rotate_angle
        self.warning_line.visible = limit_value > 0
        self.warning_line.update()

    def __create_ring(self):
        self.green_section = ft.PieChartSection(
            0, color=ft.Colors.GREEN, radius=self.outer_radius)

        self.grey_section = ft.PieChartSection(
            360 - hide_section, color=ft.Colors.GREY_200, radius=self.outer_radius)

        placeholder_section = ft.PieChartSection(
            hide_section, color=ft.Colors.SURFACE, radius=self.outer_radius)

        self.ring = ft.PieChart(
            sections_space=0,
            sections=[
                self.green_section,
                self.grey_section,
                placeholder_section
            ],
            start_degree_offset=135,
            center_space_radius=self.outer_center_space_radius,
            # expand=True
        )

    def __create_center(self):
        container_width = self.outer_center_space_radius * 2
        left = self.max_radius - container_width * 0.5
        top = left
        font_size = self.max_radius * 0.25
        unit_size = self.max_radius * 0.18

        self.center_text = ft.Text(
            value="0", size=font_size, color=ft.Colors.INVERSE_SURFACE)

        self.center_unit = ft.Text(
            value=self.unit, size=unit_size, color=ft.Colors.INVERSE_SURFACE)

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

    def __create_warning_line(self):
        self.warning_line_rotate = ft.transform.Rotate(
            angle=0,
            alignment=ft.alignment.center_left
        )
        self.warning_line = ft.Container(
            width=self.max_radius,
            height=self.max_radius * 0.02,
            left=self.max_radius,
            top=self.max_radius,
            bgcolor=ft.Colors.RED,
            visible=False,
            rotate=self.warning_line_rotate
        )

    def build(self):
        self.__create_warning_line()
        self.__create_ring()
        self.__create_center()

        main_content = ft.Stack(
            controls=[
                self.ring,
                self.warning_line,
                self.center
            ],
            width=self.max_radius * 2,
            height=self.max_radius * 2
        )

        cutting_content = ft.Stack(
            width=self.max_radius * 2,
            height=self.max_radius * 2 * 0.85,
            controls=[ft.Container(content=main_content, top=0)]
        )

        heading_content = ft.Text(
            self.heading,
            size=self.max_radius * 0.2,
            weight=ft.FontWeight.W_600
        )

        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            # expand=True,
            controls=[
                heading_content,
                cutting_content
            ])
