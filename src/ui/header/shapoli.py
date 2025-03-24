import flet as ft
from db.models.system_settings import SystemSettings


class ShaPoLi(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_settings()

    def __load_settings(self):
        system_settings = SystemSettings.get_or_none()
        if system_settings is None:
            return
        self.sha_po_li = system_settings.sha_po_li

    def build(self):
        icon = ft.Icons.CLOUD_OFF_OUTLINED
        icon_color = ft.Colors.GREY

        if self.sha_po_li:
            icon = ft.Icons.CLOUD_DONE_OUTLINED
            icon_color = ft.Colors.GREEN

        self.content = ft.TextButton(icon=icon,
                                     icon_color=icon_color,
                                     text="ShaPoLi",
                                     style=ft.ButtonStyle(
                                         color=ft.Colors.INVERSE_SURFACE,
                                         icon_size=30,
                                         text_style=ft.TextStyle(
                                             size=18
                                         )
                                     ),
                                     disabled=True)
