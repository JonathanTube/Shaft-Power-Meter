import flet as ft

from ..common.custom_card import create_card


class ReportList(ft.Column):
    def __init__(self):
        super().__init__()
        self.__create_search_card()
        self.__create_table_card()
        self.controls = [self.search_card, self.table_card]
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True

    def __create_search_card(self):
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

    def __create_table_card(self):
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

        self.table_card = ft.Card(
            expand=True,
            content=self.data_table
        )
