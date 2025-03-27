import datetime
import flet as ft


class DateTimeRange(ft.Row):
    def __init__(self):
        super().__init__()
        self.width = 400
        self.start_date = ft.TextField(
            expand=True,
            label="Start Date",
            hint_text="Select Start Date",
            show_cursor=False,
            autofocus=False,
            read_only=True,
            enable_interactive_selection=False,
            on_click=lambda e: e.page.open(ft.DatePicker(on_change=self.__handle_start_date_change)))

        self.end_date = ft.TextField(
            expand=True,
            label="End Date",
            hint_text="Select End Date",
            show_cursor=False,
            autofocus=False,
            read_only=True,
            enable_interactive_selection=False,
            on_click=lambda e: e.page.open(ft.DatePicker(on_change=self.__handle_end_date_change)))

        self.controls = [
            self.start_date,
            self.end_date
        ]

    def __handle_start_date_change(self, e):
        self.start_date.value = e.control.value.strftime("%Y-%m-%d")
        self.start_date.update()

    def __handle_end_date_change(self, e):
        self.end_date.value = e.control.value.strftime('%Y-%m-%d')
        self.end_date.update()

    def get_date_range(self):
        return self.start_date.value, self.end_date.value
