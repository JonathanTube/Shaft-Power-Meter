import flet as ft


class CustomCard(ft.Card):
    def __init__(self, heading: str, body: ft.Control, col={"md": 6}, expand: bool = False, height: int = None):
        super().__init__()
        self.heading = heading
        self.body = body

        self.col = col
        self.expand = expand
        self.height = height

    def build(self):
        self.content = ft.Container(
            padding=ft.padding.symmetric(10, 10),
            expand=self.expand,
            content=ft.Column(
                expand=self.expand,
                spacing=0,
                controls=[
                    ft.Container(
                        expand=False,
                        padding=ft.padding.only(bottom=10),
                        content=ft.Row(
                            expand=False,
                            controls=[
                                ft.Icon(name=ft.Icons.CYCLONE),
                                ft.Text(
                                    self.heading,
                                    weight=ft.FontWeight.BOLD,
                                    size=16
                                )
                            ]
                        )
                    ),
                    ft.Container(
                        expand=False,
                        padding=ft.padding.symmetric(0, 20),
                        content=self.body
                    )
                ]
            )
        )
