import logging
import flet as ft
from common.global_data import gdata


class DateTimeRange(ft.Row):
    def build(self):
        try:
            if self.page and self.page.session:
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
        except:
            logging.exception('exception occured at DateTimeRange.build')

    def __handle_start_date_change(self, e):
        try:
            if e.control is not None and e.control.value is not None:
                if self.start_date and self.start_date.page:
                    self.start_date.value = e.control.value.strftime(gdata.configDateTime.date_format)
                    self.start_date.update()
        except:
            logging.exception('exception occured at DateTimeRange.__handle_start_date_change')

    def __handle_end_date_change(self, e):
        try:
            if e.control is not None and e.control.value is not None:
                if self.end_date and self.end_date.page:
                    self.end_date.value = e.control.value.strftime(gdata.configDateTime.date_format)
                    self.end_date.update()
        except:
            logging.exception('exception occured at DateTimeRange.__handle_end_date_change')

    def get_date_range(self):
        if self.start_date and self.end_date:
            return self.start_date.value, self.end_date.value
        return '', ''
