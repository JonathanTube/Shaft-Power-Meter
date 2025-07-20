import logging
import flet as ft
import os
from pathlib import Path


class HeaderLogo(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def get_src(self):
        try:
            # Get absolute path to ensure reliability
            base_dir = Path(__file__).parent.parent.parent
            if self.page is not None and self.page.theme_mode == ft.ThemeMode.LIGHT:
                return os.path.join(base_dir, "assets", "logo_dark.png")
            else:
                return os.path.join(base_dir, "assets", "logo_light.png")
        except:
            logging.exception('exception occured at HeaderLogo.get_src')

    def update_style(self):
        try:
            if self.content and self.content.page:
                self.content.src = self.get_src()
                self.content.update()
        except:
            logging.exception('exception occured at HeaderLogo.update_style')

    def before_update(self):
        try:
            self.content = ft.Image(src=self.get_src(), fit=ft.ImageFit.FILL)
        except:
            logging.exception('exception occured at HeaderLogo.before_update')
