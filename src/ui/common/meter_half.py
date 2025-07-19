import logging
import flet as ft


class MeterHalf(ft.Container):
    def __init__(self, radius: int = 225, green: int = 0, orange: int = 0, red: int = 0):
        super().__init__()
        self.max_radius = radius
        self.green = green
        self.orange = orange
        self.red = red
        self.outer_radius = radius * 0.35
        self.outer_center_space_radius = radius - self.outer_radius

        self.inner_radius = self.outer_center_space_radius * 0.05
        self.inner_center_space_radius = (self.outer_center_space_radius - self.inner_radius) * 0.9

    def build(self):
        try:
            self.__create_outer()
            self.__create_inner()
            self.__create_center()
            meter = ft.Stack(
                controls=[self.outer, self.inner, self.center],
                width=self.max_radius * 2,
                height=self.max_radius * 2,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
            # 搞这么复杂就是为了隐藏下半圆
            self.content = ft.Stack(
                width=self.max_radius * 2,
                height=self.max_radius,
                controls=[ft.Container(content=meter, top=0)]
            )
        except:
            logging.exception('exception occured at MeterHalf.build')

    def set_outer_value(self, active_value: int, inactive_value: int):
        try:
            _active_value = round(active_value, 2)
            _inactive_value = round(inactive_value, 2)
            total = _active_value + _inactive_value
            if total > 0:
                self.active_part.value = _active_value / total * 180
                self.inactive_part.value = _inactive_value / total * 180

            # set outer color
            self.__set_outer_color()
            if self.outer and self.outer.page:
                self.outer.update()
        except:
            logging.exception('exception occured at MeterHalf.set_outer_value')

    def __set_outer_color(self):
        if self.active_part and self.inner_green and self.inner_orange:

            if self.active_part.value <= self.inner_green.value:
                self.active_part.color = ft.Colors.GREEN
                return

            if self.active_part.value <= self.inner_orange.value + self.inner_green.value:
                self.active_part.color = ft.Colors.ORANGE
                return

            self.active_part.color = ft.Colors.RED

    def set_center_value(self, value: int):
        try:
            if self.center_text and self.center_text.page:
                self.center_text.value = value
                self.center.update()
        except:
            logging.exception('exception occured at MeterHalf.set_center_value')
  

    def __create_outer(self):
        try:
            self.active_part = ft.PieChartSection(0, color=ft.Colors.GREEN, radius=self.outer_radius)
            self.inactive_part = ft.PieChartSection(180, color=ft.Colors.GREY_200, radius=self.outer_radius)
            self.outer = ft.PieChart(
                sections_space=0,
                sections=[
                    self.active_part,
                    self.inactive_part,
                    ft.PieChartSection(180, color=ft.Colors.SURFACE, radius=self.outer_radius)
                ],
                start_degree_offset=180,
                center_space_radius=self.outer_center_space_radius,
                expand=True
            )
        except:
            logging.exception('exception occured at MeterHalf.__create_outer')


    def __create_inner(self):
        try:
            _green = 0
            _orange = 0
            _red = 0

            total = self.green + self.orange + self.red
            if total > 0:
                _green = self.green / total * 180
                _orange = self.orange / total * 180
                _red = self.red / total * 180

            self.inner_green = ft.PieChartSection(_green, color=ft.Colors.GREEN, radius=self.inner_radius)
            self.inner_orange = ft.PieChartSection(_orange, color=ft.Colors.ORANGE, radius=self.inner_radius)
            self.inner_red = ft.PieChartSection(_red, color=ft.Colors.RED, radius=self.inner_radius)

            self.inner = ft.PieChart(
                sections_space=0,
                sections=[
                    self.inner_green,
                    self.inner_orange,
                    self.inner_red,
                    ft.PieChartSection(180, color=ft.Colors.SURFACE, radius=self.inner_radius)
                ],
                start_degree_offset=180,
                center_space_radius=self.inner_center_space_radius,
                expand=True
            )
        except:
            logging.exception('exception occured at MeterHalf.__create_inner')


    def __create_center(self):
        try:
            container_width = self.inner_center_space_radius * 2 * 0.8
            left = self.max_radius - container_width * 0.5
            top = self.inner_center_space_radius
            font_size = self.max_radius * 0.25

            self.center_text = ft.Text(value=0, size=font_size,
                                    text_align=ft.TextAlign.CENTER,
                                    color=ft.Colors.INVERSE_SURFACE)

            self.center = ft.Container(
                content=self.center_text,
                width=container_width,
                left=left,
                top=top
            )
        except:
            logging.exception('exception occured at MeterHalf.__create_center')

