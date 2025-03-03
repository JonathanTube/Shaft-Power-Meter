import flet as ft


def main(page: ft.Page):
    normal_radius = 120
    hover_radius = 130

    def on_chart_event(e: ft.PieChartEvent):
        for idx, section in enumerate(chart.sections):
            if idx == e.section_index:
                section.radius = hover_radius
            else:
                section.radius = normal_radius
        chart.update()

    chart = ft.PieChart(
        start_degree_offset=0,
        sections=[
            ft.PieChartSection(
                180,
                color=None,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                60,
                color=ft.Colors.YELLOW,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                60,
                color=ft.Colors.PURPLE,
                radius=normal_radius,
            ),
            ft.PieChartSection(
                60,
                color=ft.Colors.GREEN,
                radius=normal_radius,
            ),
        ],
        sections_space=0,
        center_space_radius=120,
        on_chart_event=on_chart_event,
        expand=True,
    )

    page.add(chart)


ft.app(main)
