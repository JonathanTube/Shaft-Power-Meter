import logging
import flet as ft
from flet_contrib.color_picker import ColorPicker


class ColorDialog(ft.IconButton):
    def __init__(self, color: str, on_change=None):
        super().__init__()
        self.on_color_change = on_change

        self.icon = ft.Icons.COLOR_LENS
        self.icon_color = color
        self.color = color
        self.icon_size = 30
        self.on_click = self.__open_color_picker
        self.col = {"xs": 6}
        self.alignment = ft.alignment.center_left

    def build(self):
        try:
            self.color_picker = ColorPicker(color=self.color, width=300)
            self.alert_dialog = ft.AlertDialog(
                content=self.color_picker,
                actions=[
                    ft.TextButton("OK", on_click=self.__change_color),
                    ft.TextButton("Cancel", on_click=self.__close_dialog)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
        except:
            logging.exception('exception occured at ColorDialog.show')

    def __open_color_picker(self, e):
        self.page.open(self.alert_dialog)

    def __change_color(self, e):
        color = self.color_picker.color

        self.icon_color = color
        self.color = color
        if callable(self.on_color_change):
            self.on_color_change(color)

        self.alert_dialog.open = False
        self.page.update()

    def __close_dialog(self, e):
        self.alert_dialog.open = False
        self.alert_dialog.update()