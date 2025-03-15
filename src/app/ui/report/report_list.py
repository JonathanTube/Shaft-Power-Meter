import flet as ft

from ..common.custom_card import create_card

class ReportList:
    def __create_search(self):
        self.search_card = create_card(
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


    def __create_data_table(self):
        self.data_table = ft.DataTable(
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
                        ft.DataCell(ft.Text("11")),
                        ft.DataCell(ft.Text("22")),
                        ft.DataCell(ft.Text("33"))
                    ])
            ])


    def create(self):
        self.__create_search()
        self.__create_data_table()
        return ft.Column(
            expand=True,
            controls=[self.search_card,self.data_table]
        )
