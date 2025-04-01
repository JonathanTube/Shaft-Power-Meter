import flet as ft

from ui.common.simple_card import SimpleCard
from .display import CounterDisplay


class CounterInterval(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        # self.bgcolor="pink"

    def build(self):
        display = CounterDisplay()

        left_time = ft.Text("00:20:12 left")

        hour_interval = ft.TextField(
            label="Interval Setting",
            suffix_text="Hours",
            text_size=12,
            size_constraints=ft.BoxConstraints(max_height=40)
        )

        started_at = ft.Text("running 0.5h starting at 08:04")

        self.content = SimpleCard(
            title="Interval",
            expand=False,
            body=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    display,
                    left_time,
                    hour_interval,
                    started_at
                ]))
