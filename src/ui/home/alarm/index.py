import flet as ft

from src.ui.common.custom_card import create_card


def _createDateTable():
    return ft.DataTable(
        expand=True,
        columns=[
            ft.DataColumn(ft.Text("No.")),
            ft.DataColumn(ft.Text("Date Time")),
            ft.DataColumn(ft.Text("Event")),
            ft.DataColumn(ft.Text("Acknowledge Time")),
            ft.DataColumn(ft.Text("Status"))
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("#1")),
                    ft.DataCell(ft.Text(11)),
                    ft.DataCell(ft.Text(22)),
                    ft.DataCell(ft.Text(33)),
                    ft.DataCell(ft.Text(44))
                ])
        ])


def _createSearch():
    return create_card(
        heading="Search",
        body=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(controls=[
                    ft.TextField(label="Start Date"),
                    ft.TextField(label="End Date")
                ]),
                ft.FilledButton("Export")
            ]))


def createAlarm():
    return ft.Column(
        expand=True,
        controls=[
            _createSearch(),
            _createDateTable()
        ])
