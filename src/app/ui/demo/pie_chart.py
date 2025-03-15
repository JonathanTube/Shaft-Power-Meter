import flet as ft


def main(page: ft.Page):
    normal_radius = 40

    chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                160,
                color=ft.Colors.GREEN,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                20,
                color=ft.Colors.GREY_200,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                180,
                color=ft.Colors.SURFACE,
                radius=normal_radius,
            )
        ],
        start_degree_offset=180,
        center_space_radius=60,
        expand=True,
    )

    page.add(chart)


ft.app(main)
