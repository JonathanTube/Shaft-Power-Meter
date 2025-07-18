import flet as ft
import logging
import screen_brightness_control as sbc
from utils.brightness_controller import BrightnessController


class Theme(ft.Container):
    def __init__(self):
        super().__init__()
        self.margin = ft.margin.symmetric(horizontal=20)
        self.brightness_ctl = None
        self.brightness_ctl_enabled = False

    def build(self):
        try:
            self.brightness = ft.Text(f"{100}%", size=30, weight=ft.FontWeight.W_500)

            self.slider = ft.Slider(
                width=300,
                expand=False, min=0, max=100, value=100,
                on_change=self.__slider_changed
            )
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
                                self.slider,
                                ft.Icon(
                                    expand=False,
                                    name=ft.icons.LIGHT_MODE_ROUNDED
                                )
                            ])
                        ])
                ))

            self.content = ft.Row([
                ft.IconButton(
                    icon=ft.Icons.LIGHT_MODE,
                    on_click=lambda _: self.toggle_theme()
                ),
                ft.IconButton(
                    icon=ft.icons.SETTINGS_BRIGHTNESS,
                    on_click=lambda _: self.page.open(self.dlg)
                )
            ])

            if not BrightnessController.is_installed():
                logging.info('AdvBrightnessDev未安装')
                return

            try:
                logging.info('AdvBrightnessDev已安装')
                self.brightness_ctl = BrightnessController()
                self.brightness_ctl.open()
                self.brightness_ctl_enabled = True
                self.slider.value = self.brightness_ctl.get_percentage()
                logging.info('AdvBrightnessDev初始化成功')
            except:
                logging.exception("AdvBrightnessUtility open failed.")
                self.brightness_ctl_enabled = False

        except:
            logging.exception('exception occured at Theme.build')

    def toggle_theme(self):
        if self.page and self.page.session:
            try:
                if self.page.theme_mode == ft.ThemeMode.LIGHT:
                    self.page.theme_mode = ft.ThemeMode.DARK
                    self.icon = ft.Icons.DARK_MODE
                else:
                    self.page.theme_mode = ft.ThemeMode.LIGHT
                    self.icon = ft.Icons.LIGHT_MODE
                self.page.update()
                self.page.appbar.update()
            except:
                logging.exception('exception occured at Theme.toggle_theme')

    def __slider_changed(self, e):
        try:
            if e.control is not None:
                value = int(e.control.value)
                if self.brightness_ctl_enabled:
                    self.brightness_ctl.set_percentage(value)
                else:
                    sbc.set_brightness(value)
                self.brightness.value = f"{int(value)}%"
                self.brightness.update()
        except:
            pass
