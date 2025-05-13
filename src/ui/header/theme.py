import os
import subprocess
import flet as ft
import screen_brightness_control as sbc
import logging

from common.control_manager import ControlManager
from ui.common.toast import Toast

default_avd = "C:\\Program Files (x86)\\Advantech\\Brightness\\Utility\\BIN\\AdvBrightnessUtility.exe"


class Theme(ft.Container):
    def __init__(self):
        super().__init__()
        self.margin = ft.margin.symmetric(horizontal=20)

    def build(self):
        self.content = ft.Row([
            ft.IconButton(icon=ft.Icons.LIGHT_MODE, on_click=self.toggle_theme),
            ft.IconButton(icon=ft.icons.SETTINGS_BRIGHTNESS, on_click=self.show_dlg)
        ])

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.icon = ft.Icons.DARK_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.icon = ft.Icons.LIGHT_MODE
        ControlManager.on_theme_change()
        self.page.update()

    def build_dlg(self):
        self.brightness = ft.Text(f"{100}%", size=30, weight=ft.FontWeight.W_500)
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

    def show_dlg(self, e):
        if os.path.exists(default_avd):
            try:
                subprocess.Popen(default_avd)
                self.page.window.minimized = True
                self.page.update()
            except Exception as e:
                logging.error(f"AdvBrightnessUtility error: {e}")
                Toast.show_error(self.page, f"the AdvBrightnessUtility.exe should be installed at {default_avd}")
        else:
            self.build_dlg()
            # brightness = sbc.get_brightness() 太卡，去掉
            # self.brightness.value = f"{brightness}%"
            e.page.open(self.dlg)

    def __slider_changed(self, e):
        sbc.set_brightness(e.control.value)
        self.brightness.value = f"{int(e.control.value)}%"
        self.brightness.update()
