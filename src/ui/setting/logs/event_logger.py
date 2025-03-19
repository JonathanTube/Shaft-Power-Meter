from db.models.event_log import EventLog
from ui.common.custom_card import create_card
import flet as ft


class EventLogger(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_data()
        self.content = self.__create()

    def __load_data(self):
        self.data = EventLog.select().order_by(EventLog.started_at.desc()).limit(10)
        self.rows = []
        for breach in self.data:
            self.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(breach.id)),
                    ft.DataCell(ft.Text(breach.breach_reason)),
                    ft.DataCell(ft.Text(breach.started_at)),
                    ft.DataCell(ft.Text(breach.ship_position_when_started)),
                    ft.DataCell(ft.Text(breach.ended_at)),
                    ft.DataCell(ft.Text(breach.ship_position_when_ended)),
                    ft.DataCell(ft.Text(breach.note))
                ])
            )

    def __create_table_card(self):
        self.table = ft.DataTable(
            expand=True,
            columns=[
                ft.DataColumn(
                    ft.Text("No.")
                ),
                ft.DataColumn(
                    ft.Text("Reason For\nPower Reserve\nBreach")
                ),
                ft.DataColumn(
                    ft.Text("Date/Time Of\nPower Reserve\nBreach")
                ),
                ft.DataColumn(
                    ft.Text("Ship Position Of\nPower Reserve\nBreach")
                ),
                ft.DataColumn(
                    ft.Text("Date/Time\nWhen Returning To\nLimited Power")
                ),
                ft.DataColumn(
                    ft.Text("Ship Position\nWhen Returning To\nLimited Power")
                ),
                ft.DataColumn(
                    ft.Text("Note")
                )
            ],
            rows=self.rows)
        self.table_card = ft.Card(
            content=self.table,
            expand=True
        )

    def __create_search_card(self):
        self.search = create_card(
            heading="Search",
            body=ft.Row(controls=[
                ft.TextField(label="Start Date"),
                ft.TextField(label="End Date")
            ]))

    def __create(self):
        self.__create_search_card()
        self.__create_table_card()
        return ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            controls=[
                self.search,
                self.table_card
            ])
