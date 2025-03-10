import flet as ft

from src.ui.common.custom_card import create_card


def _createItem(label: str, value: str, unit: str = ''):
    value_and_unit = ft.Row(
        vertical_alignment=ft.VerticalAlignment.END,
        controls=[
            ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
            ft.Text(unit, size=12, color=ft.Colors.GREY_600,
                    width=40, bgcolor=ft.Colors.GREEN_200)
        ])

    return ft.Row(
        vertical_alignment=ft.VerticalAlignment.END,
        # similar to justify-content of css.
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Text(label, size=14, text_align=ft.TextAlign.RIGHT, width=140),
            value_and_unit
        ])


def createDisplay(sum_power: float, average_power: float, revolution: int, average_revolution: int):
    return ft.Column(
        controls=[
            _createItem('Sum Power', sum_power, 'kWh'),
            _createItem('Average Power', average_power, 'kWh'),
            _createItem('Revolution', revolution),
            _createItem('Average Revolution', average_revolution, 'rpm')
        ])
