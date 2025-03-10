import flet as ft

from ui.common.custom_card import createCard


def _createSearch():
    return createCard(
        heading="Search",
        body=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(controls=[
                    ft.TextField(label="Start Date"),
                    ft.TextField(label="End Date")
                ]),
                ft.FilledButton("New Report")
            ]))


def _createDateTable():
    return ft.DataTable(
        expand=True,
        width=4000,
        columns=[
            ft.DataColumn(ft.Text("No.")),
            ft.DataColumn(ft.Text("Report Name")),
            ft.DataColumn(ft.Text("Create At")),
            ft.DataColumn(ft.Text("Operation"))
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("#1")),
                    ft.DataCell(ft.Text(11)),
                    ft.DataCell(ft.Text(22)),
                    ft.DataCell(ft.Text(33))
                ])
        ])


def createReport():
    return ft.Column(
        expand=True,
        controls=[
            _createSearch(),
            _createDateTable()
        ])
