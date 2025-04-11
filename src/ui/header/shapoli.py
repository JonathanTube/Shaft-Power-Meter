import flet as ft
from db.models.system_settings import SystemSettings


class ShaPoLi(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.only(right=10)
        self.system_settings = SystemSettings.get()
        self.sha_po_li = self.system_settings.sha_po_li

    def switch(self):
        if self.sha_po_li:
            self.content.icon = ft.Icons.CLOUD_DONE_OUTLINED
            self.content.icon_color = ft.Colors.GREEN
        else:
            self.content.icon = ft.Icons.CLOUD_OFF_OUTLINED
            self.content.icon_color = ft.Colors.GREY
        self.content.update()

    def build(self):
        self.content = ft.TextButton(
            icon=ft.Icons.CLOUD_OFF_OUTLINED,
            icon_color=ft.Colors.GREY,
            text="ShaPoLi",
            disabled=True,
            style=ft.ButtonStyle(
                color=ft.Colors.INVERSE_SURFACE,
                icon_size=30,
                text_style=ft.TextStyle(
                    size=18
                )
            ))

    def did_mount(self):
        self.switch()
