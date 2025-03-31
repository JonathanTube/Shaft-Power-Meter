import flet as ft

from ui.common.custom_card import CustomCard
from .display import CounterDisplay


class CounterTotal(ft.Container):
    def __init__(self, title: str = None):
        super().__init__()
        self.title = title

        self.expand = True

    def build(self):
        display = CounterDisplay()
        time_elapsed = ft.Text("00 d 23:10:01 h measured")
        started_at = ft.Text("started at 18/07/2014 06:56:19")

        self.content = CustomCard(
            heading=self.title,
            expand=True,
            body=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    display,
                    time_elapsed,
                    started_at
                ]))
