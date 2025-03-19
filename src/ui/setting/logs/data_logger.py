import flet as ft
from ui.common.custom_card import create_card
from db.models.data_log import DataLog


class DataLogger(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_data()
        self.content = self.__create()

    def __load_data(self):
        self.data = DataLog.select().order_by(DataLog.id.desc()).limit(10)
        self.rows = []
        for item in self.data:
            self.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item.id)),
                    ft.DataCell(ft.Text(f"{item.utc_date} {item.utc_time}")),
                    ft.DataCell(ft.Text(f"{item.revolution}")),
                    ft.DataCell(ft.Text(f"{item.thrust}")),
                    ft.DataCell(ft.Text(f"{item.torque}")),
                    ft.DataCell(ft.Text(f"{item.power}"))
                ])
            )

    def __create_table(self):
        self.table = ft.DataTable(
            expand=True,
            columns=[
                ft.DataColumn(ft.Text("No.")),
                ft.DataColumn(ft.Text("Date Time")),
                ft.DataColumn(ft.Text("Revolution(Rev/Min)")),
                ft.DataColumn(ft.Text("Thrust(kN)")),
                ft.DataColumn(ft.Text("Torque(kNm)")),
                ft.DataColumn(ft.Text("Power(kW)"))
            ],
            rows=self.rows
        )
        self.table_card = ft.Card(
            content=self.table,
            expand=True
        )

    def __create_search(self):
        self.search_start_date = ft.TextField(label="Start Date", height=40)
        self.search_end_date = ft.TextField(label="End Date", height=40)
        self.search_button = ft.FilledButton(
            text="Search",
            icon=ft.icons.SEARCH,
            height=40,
            on_click=lambda _: self.__load_data()
        )
        self.search_card = create_card(
            heading="Search",
            body=ft.Row(
                controls=[
                    self.search_start_date,
                    self.search_end_date,
                    self.search_button
                ]))

    def __create(self):
        self.__create_search()
        self.__create_table()
        return ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=5,
            expand=True,
            controls=[
                self.search_card,
                self.table_card
            ])
