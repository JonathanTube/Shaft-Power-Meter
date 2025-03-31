import flet as ft

from ui.common.custom_card import CustomCard
from .display import CounterDisplay


class CounterInterval(ft.Container):
    def __init__(self, title: str = ""):
        super().__init__()
        self.title = title
        self.expand = True

    def build(self):
        display = CounterDisplay()

        left_time = ft.Text(
            "00:20:12 left", weight=ft.FontWeight.BOLD, bgcolor=ft.Colors.GREEN_200)

        hour_interval = ft.TextField(
            label="Interval Setting",
            suffix_text="h",
            prefix_icon=ft.Icons.PUNCH_CLOCK_OUTLINED
        )

        started_at = ft.Text("running 0.5h starting at 08:04")

        self.content = CustomCard(
            heading=self.title,
            body=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    display,
                    left_time,
                    hour_interval,
                    started_at
                ]))
