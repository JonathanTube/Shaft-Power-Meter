import base64
import os
import flet as ft


class HeaderLogo(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        src_base64 = self.get_src()
        self.content: ft.Image = ft.Image(src_base64=src_base64, width=100, height=100, fit=ft.ImageFit.CONTAIN)

    def get_src(self):
        BASE_DIR = os.path.dirname(__file__)   # 当前 logo.py 所在目录
        ASSETS_DIR = os.path.join(BASE_DIR, "..", "..", "assets")  # ../../assets

        if self.content and self.content.page:
            if self.content.page.theme_mode == ft.ThemeMode.LIGHT:
                path = os.path.join(ASSETS_DIR, "logo_dark.png")
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")

        # 读取本地图片并转成 base64
        path = os.path.join(ASSETS_DIR, "logo_light.png")
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def before_update(self):
        if self.content and self.content.page:
            self.content.src_base64 = self.get_src()
