import flet as ft


class DateTimeRange(ft.Row):
    def build(self):
        self.start_date = ft.TextField(
            expand=True,
            label=self.page.session.get("lang.common.start_date"),
            size_constraints=ft.BoxConstraints(max_width=200),
            can_request_focus=False,
            enable_interactive_selection=False,
            on_click=lambda e: e.page.open(ft.DatePicker(on_change=self.__handle_start_date_change)))

        self.end_date = ft.TextField(
            expand=True,
            label=self.page.session.get("lang.common.end_date"),
            size_constraints=ft.BoxConstraints(max_width=200),
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
