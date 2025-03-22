import flet as ft

from ui.common.meter_half import MeterHalf


class EEXILimitedPower(ft.Card):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.container_width = width
        self.container_height = height

    def build(self):
        meter_radius = self.container_width * 0.46
        column = ft.Column(
            expand=True,
            spacing=self.container_height * 0.1,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    'EEXI Limited Power(%)',
                    weight=ft.FontWeight.BOLD,
                    size=20
                ),
                MeterHalf(radius=meter_radius)
            ])

        container = ft.Container(
            content=column,
            alignment=ft.alignment.center,
            padding=10,
            width=self.container_width + 10,
            height=self.container_height
        )

        self.content = container
