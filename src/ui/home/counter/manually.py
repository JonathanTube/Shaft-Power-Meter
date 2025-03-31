import flet as ft

from ui.common.simple_card import SimpleCard
from .display import CounterDisplay


class CounterManually(ft.Container):
    def __init__(self, title: str = ""):
        super().__init__()
        self.title = title

        self.expand = True

    def build(self):
        display = CounterDisplay()

        stopped_at = ft.Text("Stopped", weight=ft.FontWeight.BOLD,
                             color=ft.Colors.RED_500)
        time_elapsed = ft.Text("00 d 23:10:01 h measured")
        started_at = ft.Text("stopped at 18/07/2014 06:56:19")

        start_button = ft.FilledButton(
            "Start", bgcolor=ft.Colors.GREEN, expand=True, width=200)

        stop_button = ft.FilledButton(
            "Stop", bgcolor=ft.Colors.RED, expand=True, width=200)

        self.content = SimpleCard(
            title=self.title,
            body=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    display,
                    ft.Divider(height=1),
                    stopped_at,
                    time_elapsed,
                    start_button,
                    started_at
                ]
            )
        )
