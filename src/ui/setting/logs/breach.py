from ui.common.custom_card import create_card
import flet as ft


class BreachLog(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__create()

    def __create_table(self):
        self.table = ft.DataTable(
            expand=True,
            columns=[
                ft.DataColumn(ft.Text("No.")),
                ft.DataColumn(ft.Text("Reason For\nPower Reserve\nBreach")),
                ft.DataColumn(ft.Text("Date/Time Of\nPower Reserve\nBreach")),
                ft.DataColumn(
                    ft.Text("Ship Position Of\nPower Reserve\nBreach")),
                ft.DataColumn(
                    ft.Text("Date/Time\nWhen Returning To\nLimited Power")),
                ft.DataColumn(
                    ft.Text("Ship Position\nWhen Returning To\nLimited Power")),
                ft.DataColumn(ft.Text("Action"))
                # ft.DataColumn(ft.Text("Reason For Power Reserve Breach")),
                # ft.DataColumn(ft.Text("Date/Time Of Power Reserve Breach")),
                # ft.DataColumn(
                #     ft.Text("Ship Position Of Power Reserve Breach")),
                # ft.DataColumn(
                #     ft.Text("Date/Time When Returning To Limited Power")),
                # ft.DataColumn(
                #     ft.Text("Ship Position When Returning To Limited Power")),
                # ft.DataColumn(ft.Text("Action"))
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

    def __create_search(self):
        self.search = create_card(
            heading="Search",
            body=ft.Row(controls=[
                ft.TextField(label="Start Date"),
                ft.TextField(label="End Date")
            ]))

    def __create(self):
        self.__create_search(),
        self.__create_table()
        return ft.Column(
            expand=True,
            controls=[
                self.search,
                self.table
            ])
