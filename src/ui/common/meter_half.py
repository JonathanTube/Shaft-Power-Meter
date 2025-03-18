import flet as ft


class MeterHalf(ft.Container):
    def __init__(self, radius: int):
        super().__init__()
        self.max_radius = radius
        self.outer_radius = radius * 0.35
        self.outer_center_space_radius = radius - self.outer_radius

        self.inner_radius = self.outer_center_space_radius * 0.05
        self.inner_center_space_radius = (self.outer_center_space_radius - self.inner_radius) * 0.9

        self.content = self.__create()

    def __create_outer(self):
        self.outer = ft.PieChart(
            sections_space=0,
            sections=[
                ft.PieChartSection(160, color=ft.Colors.GREEN, radius=self.outer_radius),
                ft.PieChartSection(20, color=ft.Colors.GREY_200, radius=self.outer_radius),
                ft.PieChartSection(180, color=ft.Colors.SURFACE, radius=self.outer_radius)
            ],
            start_degree_offset=180,
            center_space_radius=self.outer_center_space_radius,
            expand=True
        )

    def __create_inner(self):
        self.inner = ft.PieChart(
            sections_space=0,
            sections=[
                ft.PieChartSection(140, color=ft.Colors.GREEN, radius=self.inner_radius),
                ft.PieChartSection(20, color=ft.Colors.ORANGE, radius=self.inner_radius),
                ft.PieChartSection(20, color=ft.Colors.RED, radius=self.inner_radius),
                ft.PieChartSection(180, color=ft.Colors.SURFACE, radius=self.inner_radius)
            ],
            start_degree_offset=180,
            center_space_radius=self.inner_center_space_radius,
            expand=True
        )

    def __create_center(self):
        container_width = self.inner_center_space_radius * 2 * 0.8
        left = self.max_radius - container_width * 0.5
        top = self.inner_center_space_radius
        font_size = self.max_radius * 0.25

        self.center_text = ft.Text(value="91", size=font_size,
                                   text_align=ft.TextAlign.CENTER,
                                   color=ft.Colors.INVERSE_SURFACE)

        self.center = ft.Container(
            content=self.center_text,
            width=container_width,
            left=left,
            top=top
        )

    def __create(self):
        self.__create_outer()
        self.__create_inner()
        self.__create_center()
        meter = ft.Stack(
            controls=[
                self.outer,
                self.inner,
                self.center
            ],
            width=self.max_radius * 2,
            height=self.max_radius * 2,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )
        # 搞这么复杂就是为了隐藏下半圆
        return ft.Stack(
            width=self.max_radius * 2,
            height=self.max_radius,
            controls=[ft.Container(content=meter, top=0)]
        )
#
#
# def main(page: ft.Page):
#     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
#     page.vertical_alignment = ft.MainAxisAlignment.CENTER
#     page.add(Meter(200).create())
#
#
# ft.app(main)
