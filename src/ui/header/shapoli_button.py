import flet as ft


class ShaPoLiButton(ft.Container):
    def __init__(self):
        super().__init__()

        row = ft.Row(
            controls=[
                ft.Icon(name=ft.Icons.CONNECTED_TV,
                        color=ft.Colors.WHITE,
                        size=30),
                ft.Text("ShaPoLi", size=20, color=ft.Colors.WHITE,
                        weight=ft.FontWeight.W_600)
            ],
            spacing=10
        )

        self.content = row
        self.margin = ft.margin.symmetric(horizontal=20)
        self.padding = ft.padding.symmetric(horizontal=12, vertical=5)
        self.bgcolor = ft.Colors.GREEN_600
        self.border_radius = 30
