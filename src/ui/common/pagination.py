import logging
from typing import Callable
import flet as ft


class Pagination(ft.Container):
    def __init__(self, total_items: int, page_size: int, on_change: Callable[[int, int], None]):
        super().__init__()
        self.page_size = page_size
        self.total = total_items
        self.total_pages = 0
        self.current_page = 1

        self.on_change = on_change

    def build(self):
        try:
            self.page_number = ft.Text(
                value=f"Page {self.current_page} of {self.total_pages}"
            )
            self.first_page_button = ft.IconButton(
                icon=ft.icons.FIRST_PAGE,
                on_click=self.on_first_page_click
            )
            self.previous_page_button = ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                on_click=self.on_previous_page_click
            )
            self.next_page_button = ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                on_click=self.on_next_page_click
            )
            self.last_page_button = ft.IconButton(
                icon=ft.icons.LAST_PAGE,
                on_click=self.on_last_page_click
            )
            self.content = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.first_page_button,
                    self.previous_page_button,
                    self.page_number,
                    self.next_page_button,
                    self.last_page_button
                ]
            )
        except:
            logging.exception('exception occured at Pagination.build')

    def on_first_page_click(self, e):
        self.current_page = 1
        self.on_change(self.current_page, self.page_size)
        self.update()

    def on_previous_page_click(self, e):
        self.current_page = max(1, self.current_page - 1)
        self.on_change(self.current_page, self.page_size)
        self.update()

    def on_next_page_click(self, e):
        self.current_page = min(self.total_pages, self.current_page + 1)
        self.on_change(self.current_page, self.page_size)
        self.update()

    def on_last_page_click(self, e):
        self.current_page = self.total_pages
        self.on_change(self.current_page, self.page_size)
        self.update()

    def go_first_page(self):
        self.current_page = 1

    def update_total(self, total: int):
        self.total = total

    def before_update(self):
        try:
            if self.page:
                self.total_pages = (self.total + self.page_size - 1) // self.page_size

                self.page_number.value = f"{self.current_page} of {self.total_pages}"
                self.visible = self.total > self.page_size

                self.page_number.value = f"{self.current_page} of {self.total_pages}"

                if self.current_page <= 1:
                    self.first_page_button.disabled = True
                    self.previous_page_button.disabled = True
                else:
                    self.first_page_button.disabled = False
                    self.previous_page_button.disabled = False

                if self.current_page >= self.total_pages:
                    self.last_page_button.disabled = True
                    self.next_page_button.disabled = True
                else:
                    self.last_page_button.disabled = False
                    self.next_page_button.disabled = False
        except:
            logging.exception('exception occured at Pagination.before_update')
