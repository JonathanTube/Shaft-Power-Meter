import flet as ft
import os
from pathlib import Path

class HeaderLogo(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):       
        self.content = ft.Image(src=self.get_src(), fit=ft.ImageFit.FILL)

    def get_src(self):
        # Get absolute path to ensure reliability
        base_dir = Path(__file__).parent.parent.parent
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            return os.path.join(base_dir, "assets", "logo_dark.png")
        else:
            return os.path.join(base_dir, "assets", "logo_light.png")
        
    def update_style(self):
        self.content.src = self.get_src()
        self.content.update()
