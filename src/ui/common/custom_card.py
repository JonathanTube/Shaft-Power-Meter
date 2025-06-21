import flet as ft


class CustomCard(ft.Card):
    def __init__(self, heading: str = None, body: ft.Control = None, col: dict[str, int] = {"md": 6}, expand: bool = False, height: int = None):
        super().__init__()
        self.heading = heading
        self.body = body
        self.margin = 0

        self.col = col
        self.expand = expand
        self.height = height

    def build(self):
        self.heading_title = ft.Text(
            self.heading,
            weight=ft.FontWeight.BOLD,
            size=16
        )
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
                                self.heading_title
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

    def before_update(self):
        self.heading_title.value = self.heading

    def set_title(self, title: str):
        self.heading = title
