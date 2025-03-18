from db.models.gps_log import GpsLog
from ui.common.custom_card import create_card
import flet as ft


class GpsLogger(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_data()
        self.content = self.__create()

    def __load_data(self):
        self.data = GpsLog.select().order_by(GpsLog.id.desc()).limit(10)
        self.rows = []
        for index, item in enumerate(self.data):
            self.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"#{index+1}")),
                    ft.DataCell(ft.Text(f"{item.utc_date} {item.utc_time}")),
                    ft.DataCell(ft.Text(f"{item.latitude}, {item.longitude}"))
                ])
            )

    def __create_table(self):
        self.table = ft.DataTable(
            width=4096,
            expand=True,
            columns=[
                ft.DataColumn(ft.Text("No.")),
                ft.DataColumn(ft.Text("UTC Date/Time")),
                ft.DataColumn(ft.Text("Ship Position"))
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
        self.search_card = create_card(
            heading="Search",
            body=ft.Row(
                controls=[
                    self.search_start_date,
                    self.search_end_date
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
