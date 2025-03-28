import flet as ft
import screen_brightness_control as sbc


class ThemeButton(ft.Container):
    def __init__(self):
        super().__init__()

    def build(self):
        sbc.set_brightness(90)
        self.brightness = ft.Text("90%", size=30, weight=ft.FontWeight.W_500)
        self.dlg = ft.AlertDialog(
            alignment=ft.alignment.center,
            content=ft.Container(
                height=100,
                expand=False,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.brightness,
                        ft.Row([
                            ft.Icon(
                                expand=False,
                                name=ft.icons.DARK_MODE_ROUNDED
                            ),
                            ft.Slider(
                                width=300,
                                expand=False, min=0, max=100, value=90,
                                on_change=self.__slider_changed
                            ),
                            ft.Icon(
                                expand=False,
                                name=ft.icons.LIGHT_MODE_ROUNDED
                            )
                        ])
                    ])
            ))

        self.margin = ft.margin.symmetric(horizontal=20)
        self.content = ft.Row([
            ft.IconButton(
                icon=ft.Icons.LIGHT_MODE,
                on_click=self.toggle_theme
            ),
            ft.IconButton(
                icon=ft.icons.SETTINGS_BRIGHTNESS,
                on_click=self.show_dlg
            )
        ])

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.icon = ft.Icons.DARK_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.icon = ft.Icons.LIGHT_MODE
        self.page.update()

    def show_dlg(self, e):
        e.page.open(self.dlg)

    def __slider_changed(self, e):
        sbc.set_brightness(e.control.value)
        self.brightness.value = f"{int(e.control.value)}%"
        self.brightness.update()
