import flet as ft
from ui.common.custom_card import create_card


class DataLogger(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__create()

    def __create_table(self):
        self.table = ft.DataTable(
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
