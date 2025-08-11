import logging
import flet as ft
from common.global_data import gdata


class ShaPoLi(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = ft.padding.only(right=10)

    def build(self):
        try:
            self.visible = gdata.configCommon.shapoli

            self.content = ft.TextButton(
                text="ShaPoLi",
                style=ft.ButtonStyle(
                    color=ft.Colors.INVERSE_SURFACE,
                    text_style=ft.TextStyle(
                        weight=ft.FontWeight.BOLD,
                        size=18
                    )
                ))
        except:
            logging.exception('exception occured at ShaPoLi.build')
