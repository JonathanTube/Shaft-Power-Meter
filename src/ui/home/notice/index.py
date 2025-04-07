import flet as ft


class Notice:
    def __init__(self):
        self.badge = None

    def create(self):
        self.badge = ft.Badge(text="0", small_size=10,
                              bgcolor=ft.Colors.GREEN,
                              text_color=ft.Colors.WHITE,
                              offset=ft.Offset(10, -10))
        return ft.Container(
            top=8, right=20,
            content=ft.Row(controls=[
                ft.FilledButton('Override', bgcolor=ft.Colors.RED,
                                color=ft.Colors.WHITE),
                ft.Text('UNREPORTED EEXI BREACHES', badge=self.badge)
            ])
        )
