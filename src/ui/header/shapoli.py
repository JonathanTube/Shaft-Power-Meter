import flet as ft
from db.models.system_settings import SystemSettings


class ShaPoLi(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.only(right=10)

    def build(self):
        self.system_settings = SystemSettings.get()
        self.sha_po_li = self.system_settings.sha_po_li

        self.content = ft.TextButton(
            text="ShaPoLi",
            visible=self.sha_po_li,
            style=ft.ButtonStyle(
                color=ft.Colors.INVERSE_SURFACE,
                icon_size=30,
                text_style=ft.TextStyle(
                    size=18
                )
            ))