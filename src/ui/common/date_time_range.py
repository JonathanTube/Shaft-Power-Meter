import datetime
import flet as ft


class DateTimeRange(ft.Row):
    def __init__(self):
        super().__init__()
        # self.width = 400
        self.start_date = ft.TextField(
            expand=True,
            label="Start Date",
            size_constraints=ft.BoxConstraints(max_width=200, max_height=40),
            can_request_focus=False,
            enable_interactive_selection=False,
            on_click=lambda e: e.page.open(ft.DatePicker(on_change=self.__handle_start_date_change)))

        self.end_date = ft.TextField(
            expand=True,
            label="End Date",
            size_constraints=ft.BoxConstraints(max_width=200, max_height=40),
            can_request_focus=False,
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

    def set_language(self):
        session = self.page.session
        self.start_date.label = session.get("lang.common.start_date")
        self.end_date.label = session.get("lang.common.end_date")

    def before_update(self):
        self.set_language()

    def did_mount(self):
        self.set_language()
