from ...common.custom_card import create_card
import flet as ft


def _createDateTable():
    return ft.DataTable(
        expand=True,
        bgcolor=ft.Colors.GREEN_300,
        columns=[
            ft.DataColumn(ft.Text("No.")),
            ft.DataColumn(ft.Text("Reason For Power Reserve Breach")),
            ft.DataColumn(ft.Text("Date/Time Of Power Reserve Breach")),
            ft.DataColumn(ft.Text("Ship Position Of Power Reserve Breach")),
            ft.DataColumn(
                ft.Text("Date/Time When Returning To Limited Power")),
            ft.DataColumn(
                ft.Text("Ship Position When Returning To Limited Power")),
            ft.DataColumn(ft.Text("Action"))
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("#1")),
                    ft.DataCell(ft.Text(11)),
                    ft.DataCell(ft.Text(22)),
                    ft.DataCell(ft.Text(33)),
                    ft.DataCell(ft.Text(44)),
                    ft.DataCell(ft.Text(55)),
                    ft.DataCell(ft.Text(66))
                ])
        ])


def _createSearch():
    return create_card(
        heading="Search",
        body=ft.Row(controls=[
            ft.TextField(label="Start Date"),
            ft.TextField(label="End Date")
        ]))


def createBreachLog():
    return ft.Column(
        expand=True,
        controls=[
            _createSearch(),
            _createDateTable()
        ])
