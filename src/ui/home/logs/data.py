import flet as ft
from src.ui.common.custom_card import create_card


def _createDateTable():
    return ft.DataTable(
        expand=True,
        columns=[
            ft.DataColumn(ft.Text("No.")),
            ft.DataColumn(ft.Text("Date/Time")),
            ft.DataColumn(ft.Text("Thrust(kN)")),
            ft.DataColumn(ft.Text("Speed(rpm)")),
            ft.DataColumn(ft.Text("Torque(kNm)")),
            ft.DataColumn(ft.Text("Power(kW)"))
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("#1")),
                    ft.DataCell(ft.Text(11)),
                    ft.DataCell(ft.Text(22)),
                    ft.DataCell(ft.Text(33)),
                    ft.DataCell(ft.Text(44)),
                    ft.DataCell(ft.Text(55))
                ])
        ])


def _createSearch():
    return create_card(
        heading="Search",
        body=ft.Row(controls=[
                    ft.TextField(label="Start Date"),
                    ft.TextField(label="End Date")
                    ]))


def createDataLog():
    return ft.Column(
        expand=True,
        controls=[
            _createSearch(),
            _createDateTable()
        ])
