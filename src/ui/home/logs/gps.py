import flet as ft

from ui.common.custom_card import createCard
import flet as ft


def _createDateTable():
    return ft.DataTable(
        expand=True,
        columns=[
            ft.DataColumn(ft.Text("No.")),
            ft.DataColumn(ft.Text("UTC Date/Time")),
            ft.DataColumn(ft.Text("Ship Position"))
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("#1")),
                    ft.DataCell(ft.Text(11)),
                    ft.DataCell(ft.Text(22))
                ])
        ])


def _createSearch():
    return createCard(
        heading="Search",
        body=ft.Row(controls=[
                    ft.TextField(label="Start Date"),
                    ft.TextField(label="End Date")
                    ]))


def createGpsLog():
    return ft.Column(
        expand=True,
        controls=[
            _createSearch(),
            _createDateTable()
        ])
