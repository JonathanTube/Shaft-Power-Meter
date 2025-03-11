import flet as ft

from src.ui.common.custom_card import create_card


class ZeroCalHis:
    def __create_search_card(self):
        self.search_card = create_card(
            heading="Search",
            body=ft.Row(
                controls=[
                    ft.TextField(label="Start Date"),
                    ft.TextField(label="End Date")
                ]
            )
        )

    def __create_table_card(self):
        self.table_card = create_card(
            heading="History",
            body=ft.DataTable(
                expand=True,
                columns=[
                    ft.DataColumn(ft.Text("No.")),
                    ft.DataColumn(ft.Text("Date And Time")),
                    ft.DataColumn(
                        ft.Text("Torque Offset(Nm)"), numeric=True),
                    ft.DataColumn(
                        ft.Text("Thrust Offset(N)"), numeric=True),
                    ft.DataColumn(
                        ft.Text("Error Ratio(%)"), numeric=True),
                    ft.DataColumn(
                        ft.Text("Accepted"))
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("#1")),
                            ft.DataCell(ft.Text(11)),
                            ft.DataCell(ft.Text(22)),
                            ft.DataCell(ft.Text(33)),
                            ft.DataCell(ft.Text(44)),
                            ft.DataCell(ft.Row(controls=[ft.Text('Yes'), ft.Icon(
                                name=ft.Icons.ASSIGNMENT_TURNED_IN_OUTLINED, size=20, color=ft.Colors.GREEN_500)]))
                        ])
                ]))

    def create(self):
        self.__create_search_card()
        self.__create_table_card()
        return ft.Column(
            controls=[
                self.search_card,
                self.table_card
            ])
