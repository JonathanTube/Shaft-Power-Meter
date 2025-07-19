import logging
import flet as ft


class CustomCard(ft.Card):
    def __init__(self, heading: str = None, body: ft.Control = None, col: dict[str, int] = {"md": 6}, expand: bool = False, height: int = None):
        super().__init__()
        self.heading = heading if heading is not None else ''
        self.body = body
        self.margin = 0

        self.col = col
        self.expand = expand
        self.height = height

    def build(self):
        try:
            self.heading_title = ft.Text(
                self.heading,
                weight=ft.FontWeight.BOLD,
                size=16
            )
            controls = [
                ft.Container(
                    expand=False,
                    padding=ft.padding.only(bottom=10),
                    content=ft.Row(
                        expand=False,
                        controls=[
                            ft.Icon(name=ft.Icons.CYCLONE),
                            self.heading_title
                        ]
                    )
                )
            ]
            if self.body is not None:
                controls.append(
                    ft.Container(
                        expand=False,
                        padding=ft.padding.symmetric(0, 20),
                        content=self.body
                    )
                )
            self.content = ft.Container(
                padding=ft.padding.symmetric(10, 10),
                expand=self.expand,
                content=ft.Column(
                    expand=self.expand,
                    spacing=0,
                    controls=controls
                )
            )
        except:
            logging.exception('exception occured at CustomCard.build')

    def before_update(self):
        try:
            if self.heading_title and self.heading_title.page:
                self.heading_title.value = self.heading
        except:
            logging.exception('exception occured at CustomCard.before_update')

    def set_title(self, title: str):
        self.heading = title if title is not None else ''
