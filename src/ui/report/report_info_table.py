import flet as ft

from db.models.report_info import ReportInfo
from ui.report.report_info_dialog import ReportInfoDialog


class ReportInfoTable(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_data()
        self.content = self.__create()
        self.padding = 5

    def __view_report(self, e, id):
        e.page.open(ReportInfoDialog(id))

    def __export_report(self, e, id):
        print(id)

    def __load_data(self):
        data = ReportInfo.select().order_by(ReportInfo.id.desc()).limit(10)
        self.rows = []
        for item in data:
            self.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(item.id)),
                ft.DataCell(ft.Text(item.report_name)),
                ft.DataCell(ft.Text(item.created_at)),
                ft.DataCell(
                    ft.Row(controls=[
                        ft.TextButton(
                            icon=ft.Icons.VISIBILITY_OUTLINED,
                            text="View",
                            on_click=lambda e: self.__view_report(e, item.id)
                        ),
                        ft.TextButton(
                            icon=ft.Icons.DOWNLOAD_OUTLINED,
                            text="Export",
                            on_click=lambda e: self.__export_report(e, item.id)
                        )
                    ])
                )
            ]))

    def __create_search_card(self):
        self.start_date = ft.TextField(label="Start Date", height=40)
        self.end_date = ft.TextField(label="End Date", height=40)
        self.search_button = ft.ElevatedButton(
            icon=ft.Icons.SEARCH_OUTLINED, text="Search", height=40)

        search_row = ft.Row(controls=[
            self.start_date,
            self.end_date,
            self.search_button
        ])
        search_container = ft.Container(content=search_row, padding=10)
        self.search_card = ft.Card(content=search_container)

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
            rows=self.rows)

        self.table_card = ft.Card(
            expand=True,
            content=self.data_table
        )

    def __create(self):
        self.__create_search_card()
        self.__create_table_card()
        return ft.Column(
            spacing=2,
            controls=[self.search_card, self.table_card],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )
