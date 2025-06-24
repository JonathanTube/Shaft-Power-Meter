import logging
import math

import flet as ft


class MeterRound(ft.Container):
    def __init__(self, heading: str, radius: int, unit: str, color: str = ft.Colors.GREEN, max: float = 0, limit: float = 0):
        super().__init__()
        self.__hide_section = 90

        self.max_value = max
        self.limit_value = limit

        self.heading = heading
        self.unit = unit
        self.max_radius = radius
        self.outer_radius = radius * 0.35
        self.outer_center_space_radius = radius - self.outer_radius

        self.color = color

    def set_data(self, actual_value: int, display_value: int, display_unit: str):
        try:
            if self.max_value == 0:
                return
            # update unit
            self.center_unit.value = display_unit
            self.center_unit.update()

            # update active section
            active_val = (360 - self.__hide_section) * actual_value / self.max_value
            # 如果value大于max_value，则active_val为360 - self.__hide_section
            if actual_value > self.max_value:
                active_val = 360 - self.__hide_section

            self.active_section.value = active_val
            self.active_section.update()

            # update inactive section
            inactive_val = (360 - self.__hide_section) - active_val
            self.inactive_section.value = inactive_val
            self.inactive_section.update()

            # update center text
            self.center_text.value = display_value
            self.center_text.update()
        except:
            logging.exception('exception occured at MeterRound.set_data')


    def __create_ring(self):
        self.active_section = ft.PieChartSection(
            0, color=self.color, radius=self.outer_radius)

        self.inactive_section = ft.PieChartSection(
            360 - self.__hide_section, color=ft.Colors.GREY_200, radius=self.outer_radius)

        placeholder_section = ft.PieChartSection(
            self.__hide_section, color=ft.Colors.SURFACE, radius=self.outer_radius)

        self.ring = ft.PieChart(
            sections_space=0,
            sections=[
                self.active_section,
                self.inactive_section,
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
        rotate_start = math.pi * 3 / 4
        rotate_propotion = self.limit_value / self.max_value
        rotate_angle = rotate_start + (2 * rotate_start) * rotate_propotion

        self.warning_line_rotate = ft.transform.Rotate(
            angle=rotate_angle,
            alignment=ft.alignment.center_left
        )
        self.warning_line = ft.Container(
            width=self.max_radius,
            height=self.max_radius * 0.02,
            left=self.max_radius,
            top=self.max_radius,
            bgcolor=ft.Colors.ORANGE_ACCENT,
            visible=self.limit_value > 0,
            rotate=self.warning_line_rotate
        )

    def build(self):
        try:
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
        except:
            logging.exception('exception occured at MeterRound.build')

