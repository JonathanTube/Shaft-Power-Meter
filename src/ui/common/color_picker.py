import flet as ft
from flet_contrib.color_picker import ColorPicker


class ColorDialog:
    def __init__(self, on_change=None):
        self.on_color_change = on_change
        self.color_icon = ft.IconButton(icon=ft.Icons.COLOR_LENS,icon_color='#c8df6f',
                                        icon_size=30, on_click=self.__open_color_picker)
        self.color_picker = ColorPicker(color='#c8df6f', width=300)

        self.alert_dialog = ft.AlertDialog(
            content=self.color_picker,
            actions=[
                ft.TextButton("OK", on_click=self.__change_color),
                ft.TextButton("Cancel", on_click=self.__close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

    def __open_color_picker(self, e):
        self.alert_dialog.open = True
        e.control.page.open(self.alert_dialog)

    def __change_color(self, e):
        color = self.color_picker.color

        self.color_icon.icon_color = color

        if callable(self.on_color_change):
            self.on_color_change(color)

        self.alert_dialog.open = False
        e.control.page.update()

    def __close_dialog(self, e):
        self.alert_dialog.open = False
        self.alert_dialog.update()

    def create(self):
        return self.color_icon

    def set_color(self,color:str):
        if color:
            self.color_icon.icon_color = color
            self.color_picker.color = color
#
# def main(page: ft.Page):
#     page.add(ColorDialog().create())
#
#
# ft.app(main)
