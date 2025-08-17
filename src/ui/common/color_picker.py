import logging
import flet as ft
from flet_contrib.color_picker import ColorPicker


class ColorDialog(ft.IconButton):
    def __init__(self, color: str, on_change=None):
        super().__init__()
        self.on_color_change = on_change

        self.icon = ft.Icons.COLOR_LENS

        self.icon_color = color or ft.Colors.BLUE
        self.color = color or ft.Colors.BLUE

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
                    ft.TextButton(self.page.session.get("lang.button.confirm"), on_click=self.__change_color),
                    ft.TextButton(self.page.session.get("lang.button.cancel"), on_click=self.__close_dialog)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
        except:
            logging.exception('exception occured at ColorDialog.show')

    def __open_color_picker(self, e):
        try:
            if self.page is not None:
                self.page.open(self.alert_dialog)
        except:
            logging.exception('exception occured at ColorDialog.__open_color_picker')

    def __change_color(self, e):
        try:
            if self.color_picker and self.color_picker.page:
                color = self.color_picker.color

                self.icon_color = color
                self.color = color

                if callable(self.on_color_change):
                    self.on_color_change(color)

                if self.alert_dialog:
                    self.alert_dialog.open = False

                if self.page:
                    self.page.update()
        except:
            logging.exception('exception occured at ColorDialog.__change_color')

    def __close_dialog(self, e):
        try:
            if self.alert_dialog and self.alert_dialog.page:
                self.alert_dialog.open = False
                self.alert_dialog.update()
        except:
            logging.exception('exception occured at ColorDialog.__close_dialog')
