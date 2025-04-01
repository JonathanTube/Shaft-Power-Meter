import flet as ft

from ui.common.simple_card import SimpleCard
from .display import CounterDisplay


class CounterTotal(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        display = CounterDisplay()
        time_elapsed = ft.Text("00 d 23:10:01 h measured")
        started_at = ft.Text("started at 18/07/2014 06:56:19")

        self.content = SimpleCard(
            title="Total",
            expand=False,
            body=ft.Column(
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    display,
                    time_elapsed,
                    started_at
                ]))
