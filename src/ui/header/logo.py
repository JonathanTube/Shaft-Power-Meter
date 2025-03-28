import flet as ft
import os
from pathlib import Path


class HeaderLogo(ft.Container):
    def __init__(self):
        super().__init__()
        # Get absolute path to ensure reliability
        base_dir = Path(__file__).parent.parent.parent
        self.src = os.path.join(base_dir, "assets", "logo.png")
        self.fit = ft.ImageFit.FILL

    def build(self):
        self.content = ft.Image(
            src=self.src,
            width=50,
            height=50
        )
