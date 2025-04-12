from typing import Callable
import flet as ft


class Pagination(ft.Container):
    def __init__(self, page_size: int, on_change: Callable[[int, int], None]):
        super().__init__()
        self.page_size = page_size
        self.total_pages = 0
        self.current_page = 1
        self.total_items = 0
        
        self.on_change = on_change

    def build(self):
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

    def on_first_page_click(self, e):
        self.current_page = 1
        self.update_page_buttons()

    def on_previous_page_click(self, e):
        self.current_page = max(1, self.current_page - 1)
        self.update_page_buttons()

    def on_next_page_click(self, e):
        self.current_page = min(self.total_pages, self.current_page + 1)
        self.update_page_buttons()

    def on_last_page_click(self, e):
        self.current_page = self.total_pages
        self.update_page_buttons()

    def update_pagination(self, total_items):
        self.total_items = total_items
        self.total_pages = (self.total_items +
                            self.page_size - 1) // self.page_size

        self.page_number.value = f"{self.current_page} of {self.total_pages}"
        self.visible = total_items > self.page_size

        self.update_page_buttons()

    def update_page_buttons(self):
        self.on_change(self.current_page, self.page_size)
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

        self.update()
