import flet as ft
from db.models.system_settings import SystemSettings


class ShaPoLi(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.only(right=10)

    def switch(self):
        system_settings = SystemSettings.get_or_none()
        if system_settings is None:
            return
        sha_po_li = system_settings.sha_po_li

        if sha_po_li:
            self.content.icon = ft.Icons.CLOUD_DONE_OUTLINED
            self.content.icon_color = ft.Colors.GREEN
        else:
            self.content.icon = ft.Icons.CLOUD_OFF_OUTLINED
            self.content.icon_color = ft.Colors.GREY

    def build(self):
        sha_po_li = ft.TextButton(icon=ft.Icons.CLOUD_OFF_OUTLINED,
                                  icon_color=ft.Colors.GREY,
                                  text="ShaPoLi",
                                  style=ft.ButtonStyle(
                                      color=ft.Colors.INVERSE_SURFACE,
                                      icon_size=30,
                                      text_style=ft.TextStyle(
                                          size=18
                                      )
                                  ),
                                  disabled=True)
        self.content = sha_po_li
        self.page.session.set("sha_po_li", self)
