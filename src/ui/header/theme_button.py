import flet as ft


class ThemeButton(ft.Container):
    def __init__(self):
        super().__init__()

        iconButton = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE,
            on_click=self.toggle_theme
        )

        self.content = iconButton
        self.margin = ft.margin.symmetric(horizontal=20)

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.icon = ft.Icons.DARK_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.icon = ft.Icons.LIGHT_MODE
        self.page.update()
