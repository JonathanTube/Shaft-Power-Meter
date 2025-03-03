import flet as ft


class HeaderLogo(ft.Image):
    def __init__(self):
        super().__init__()
        self.src = "src/assets/img/logo.png"
        # self.width = 180
        # self.height = 40
        self.fit = ft.ImageFit.FILL
