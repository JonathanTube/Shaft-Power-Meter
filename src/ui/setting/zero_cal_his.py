import flet as ft

from db.models.zero_cal_info import ZeroCalInfo
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast


class ZeroCalHis:
    def __load_data(self):
        start_value = self.start_date.value
        end_value = self.end_date.value

        if start_value and end_value:
            zero_cal_infos = (ZeroCalInfo.select()
                              .where(ZeroCalInfo.utc_date_time >= start_value,
                                     ZeroCalInfo.utc_date_time <= end_value)
                              .order_by(ZeroCalInfo.id.desc()).limit(10))
        else:
            zero_cal_infos = (
                ZeroCalInfo.select().order_by(ZeroCalInfo.id.desc()))

        table_rows = []
        for item in zero_cal_infos:
            state_name = 'Processing'
            if item.state == 1:
                state_name = 'Accepted'
            if item.state == 2:
                state_name = 'Aborted'

            table_rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(f"#{item.id}")),
                    ft.DataCell(ft.Text(item.torque_offset)),
                    ft.DataCell(ft.Text(item.thrust_offset)),
                    ft.DataCell(ft.Text(item.torque_error_ratio)),
                    ft.DataCell(ft.Text(item.thrust_error_ratio)),
                    ft.DataCell(ft.Text(state_name))
                ]))

        self.table_rows = table_rows

    def __handle_start_date_change(self, e):
        self.start_date.value = e.control.value.strftime('%Y-%m-%d')
        self.start_date.update()

    def __handle_end_date_change(self, e):
        self.end_date.value = e.control.value.strftime('%Y-%m-%d')
        self.end_date.update()

    def __handle_submit(self, e):
        self.__load_data()
        self.table.rows = self.table_rows
        self.table.update()
        Toast.show_success(e.page, message="Submitted")

    def __create_search_card(self):
        self.start_date = ft.TextField(
            label="Start Date",
            on_click=lambda e: e.page.open(ft.DatePicker(on_change=self.__handle_start_date_change)))

        self.end_date = ft.TextField(
            label="End Date",
            on_click=lambda e: e.page.open(ft.DatePicker(on_change=self.__handle_end_date_change)))

        self.query_button = ft.FilledButton(
            "submit", width=120, height=40, on_click=self.__handle_submit)

        self.search_card = CustomCard(
            heading="Search",
            body=ft.Row(
                controls=[
                    self.start_date,
                    self.end_date,
                    self.query_button
                ]
            )
        )

    def __create_table_card(self):
        self.__load_data()
        self.table = ft.DataTable(
            expand=True,
            heading_row_height=50,
            data_row_min_height=40,
            data_row_max_height=40,
            width=4096,
            columns=[
                ft.DataColumn(ft.Text("No.")),
                ft.DataColumn(ft.Text("Date And Time")),
                ft.DataColumn(ft.Text("Torque Offset"), numeric=True),
                ft.DataColumn(ft.Text("Thrust Offset"), numeric=True),
                ft.DataColumn(ft.Text("Error Ratio(%)"), numeric=True),
                ft.DataColumn(ft.Text("State"))
            ],
            rows=self.table_rows)

        self.table_card = CustomCard(
            heading="History",
            expand=True,
            body=self.table)

    def create(self):
        self.__create_search_card()
        self.__create_table_card()
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                self.search_card,
                self.table_card
            ])
