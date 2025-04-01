import flet as ft

from ui.common.simple_card import SimpleCard
from .display import CounterDisplay


class CounterManually(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand=True

    def build(self):
        display = CounterDisplay()

        stopped_at = ft.Text("Stopped", weight=ft.FontWeight.BOLD,
                             color=ft.Colors.RED_500)
        time_elapsed = ft.Text("00 d 23:10:01 h measured")
        stopped_at = ft.Text("stopped at 18/07/2014 06:56:19")

        start_button = ft.FilledButton(
            "Start", bgcolor=ft.Colors.GREEN, width=200)

        stop_button = ft.FilledButton("Stop", bgcolor=ft.Colors.RED, width=200)

        self.content = SimpleCard(
            title="Manually",
            expand=False,
            body=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    display,
                    stopped_at,
                    time_elapsed,
                    start_button
                    # stopped_at
                ]
            )
        )
