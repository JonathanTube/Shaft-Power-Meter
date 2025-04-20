import flet as ft

from db.models.alarm_log import AlarmLog
from ui.common.datetime_search import DatetimeSearch
from ui.common.toast import Toast
from ui.home.alarm.alarm_table import AlarmTable
from common.global_data import gdata


class AlarmList(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

    def build(self):
        search = DatetimeSearch(self.__on_search)
        self.table = AlarmTable(10, show_checkbox_column=True)

        self.ack_button = ft.FilledButton(
            text=self.page.session.get("lang.alarm.acknowledge"),
            on_click=self.__on_acknowledge
        )
        self.content = ft.Column(
            expand=False,
            spacing=5,
            controls=[
                search,
                self.table,
                self.ack_button
            ]
        )

    def __on_acknowledge(self, e):
        # get selected rows
        selected_rows = [item for item in self.table.data_table.rows if item.selected]
        if len(selected_rows) == 0:
            Toast.show_error(self.page, self.page.session.get("lang.alarm.please_select_at_least_one_alarm"))
            return
        for row in selected_rows:
            AlarmLog.update(
                acknowledge_time=gdata.utc_date_time).where(
                AlarmLog.id == row.cells[0].data).execute()

        self.table.search()
        Toast.show_success(self.page)

    def __on_search(self, start_date: str, end_date: str):
        self.table.search(start_date=start_date, end_date=end_date)
