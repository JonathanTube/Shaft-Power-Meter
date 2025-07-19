import logging
import flet as ft


class SimpleCard(ft.Container):
    def __init__(self,
                 title: str = "",
                 body: ft.Control = None,
                 text_center: bool = False,
                 body_bottom_right: bool = True,
                 expand: bool = True):
        super().__init__()
        self.expand = expand
        self.margin = 0
        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(
            width=0.5,
            color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)   
        )

        self._title = title
        self._body = body
        self._body_bottom_right = body_bottom_right
        self._text_center = text_center

    def build(self):
        try:
            title_container = ft.Container(
                visible=self._title is not None and self._title != "",
                expand=False,
                alignment=ft.alignment.center if self._text_center else ft.alignment.top_left,
                content=ft.Text(
                    value=self._title,
                    weight=ft.FontWeight.W_500,
                    size=16
                )
            )

            self.content = ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    title_container,
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.bottom_right if self._body_bottom_right else ft.alignment.center,
                        content=self._body
                    )
                ]
            )
        except:
            logging.exception('exception occured at SimpleCard.build')


    def set_title(self, title: str):
        self._title = title
