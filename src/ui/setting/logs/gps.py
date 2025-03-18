from ui.common.custom_card import create_card
import flet as ft


class GpsLog(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__create()

    def __create_table(self):
        self.table = ft.DataTable(
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

    def __create_search(self):
        self.search = create_card(
            heading="Search",
            body=ft.Row(controls=[
                        ft.TextField(label="Start Date"),
                        ft.TextField(label="End Date")
                        ]))

    def __create(self):
        self.__create_search()
        self.__create_table()
        return ft.Column(
            expand=True,
            controls=[
                self.search,
                self.table
            ])
