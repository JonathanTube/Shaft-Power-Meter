import flet as ft


class SimpleCard(ft.Card):
    def __init__(self, title: str, body: ft.Control):
        super().__init__()
        self.expand = True
        self.margin = 0
        
        self._title = title
        self._body = body

    def build(self):
        self.content = ft.Container(
            padding=ft.padding.all(10),
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text(
                        self._title,
                        weight=ft.FontWeight.W_600,
                        size=20
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.bottom_right,
                        content=self._body
                    )
                ]
            ))
