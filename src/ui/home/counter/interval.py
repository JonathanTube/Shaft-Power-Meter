import flet as ft

from ui.common.custom_card import createCard


def _createItem(label: str, value: str, unit: str = ''):
    with_unit_control = ft.Row(
        vertical_alignment=ft.VerticalAlignment.END,
        controls=[
            ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
            ft.Text(unit, size=12, color=ft.Colors.GREY_600)
        ])

    return ft.Row(
        vertical_alignment=ft.VerticalAlignment.END,
        run_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Text(label, size=14, text_align=ft.TextAlign.RIGHT, width=140),
            with_unit_control if unit else ft.Text(
                value, size=28, weight=ft.FontWeight.BOLD)
        ])


def createInterval():
    return createCard(
        heading="Interval",
        expand=True,
        body=ft.Container(content=ft.Column(
            controls=[
                _createItem('Sum Power', 111, 'kWh'),
                _createItem('Average Power', 222, 'kWh'),
                _createItem('Revolution', 333),
                _createItem('Average Revolution', 444, 'rpm')
            ]
        )))
