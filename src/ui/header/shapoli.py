import flet as ft
from db.models.system_settings import SystemSettings


class ShaPoLi(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.only(right=10)

    def build(self):
        self.system_settings: SystemSettings = SystemSettings.get()
        self.visible = self.system_settings.sha_po_li

        self.content = ft.TextButton(
            text="ShaPoLi",
            style=ft.ButtonStyle(
                color=ft.Colors.INVERSE_SURFACE,
                text_style=ft.TextStyle(
                    weight=ft.FontWeight.BOLD,
                    size=18
                )
            ))
