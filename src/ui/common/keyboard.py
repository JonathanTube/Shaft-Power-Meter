import flet as ft
from typing import Literal


class Keyboard(ft.Stack):
    def __init__(self):
        super().__init__()
        self.visible = False
        self.opened = False
        self.words = ""
        self.type = 'float'
        self.expand = True

        self.tf: ft.TextField | None = None

    def build(self):
        number_keys = [ft.OutlinedButton(str(i), col={"xs": 4}, on_click=self.__on_key_click) for i in range(1, 10)]
        number_keys.append(ft.OutlinedButton(str(0), col={"xs": 4}, on_click=self.__on_key_click))

        self.point = ft.OutlinedButton('.', col={"xs": 4}, on_click=self.__on_key_click)
        number_keys.append(self.point)

        number_keys.append(ft.OutlinedButton(icon=ft.Icons.BACKSPACE_OUTLINED, col={"xs": 4}, on_click=self.__on_delete_one, on_long_press=self.__on_delete_all))

        kb_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(content=ft.Icon(ft.Icons.KEYBOARD_OUTLINED, size=30), padding=ft.padding.only(left=10)),
                ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, on_click=self.__on_close)
            ]
        )
        self.kb = ft.Column(
            spacing=0,
            controls=[
                kb_header,
                ft.Divider(height=1),
                ft.Container(content=ft.ResponsiveRow(number_keys), padding=10)
            ]
        )
        self.kb_open = ft.Container(
            width=200,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE)),
            shadow=ft.BoxShadow(
                color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
                blur_radius=20,
                offset=ft.Offset(0, 5)
            ),
            content=self.kb
        )

        self.kb_close = ft.IconButton(icon=ft.Icons.KEYBOARD_OUTLINED, on_click=self.__on_open)

        self.gd = ft.GestureDetector(
            right=10,
            bottom=10,
            expand=False,
            mouse_cursor=ft.MouseCursor.MOVE,
            drag_interval=10,
            on_pan_update=self.__on_pan_update,
            content=self.kb_close
        )

        self.controls = [self.gd]

    def show(self):
        self.visible = True
        self.update()

    def open(self, text_field: ft.TextField, type: Literal['int', 'float', 'ip'] = 'float'):
        self.show()
        # recovery the border color of last text field
        try:
            self.tf.border_color = ft.Colors.BLACK
            self.tf.update()
        except:
            pass

        if text_field is not None:
            self.words = str(text_field.value)            

        if not self.opened:
            self.__on_open(None)

        self.type = type
        self.point.visible = self.type == 'float' or self.type == 'ip'
        self.point.update()

        self.tf = text_field
        # set the border color of current text field
        if self.tf is not None:
            self.tf.border_color = ft.Colors.PRIMARY
            self.tf.update()

    def close(self):
        self.visible = False
        self.update()
        self.__on_close(None)

    def __on_open(self, e):
        self.opened = True
        self.gd.content = self.kb_open
        self.gd.left = 500
        self.gd.top = 250
        self.gd.right = None
        self.gd.bottom = None
        self.gd.update()

    def __on_close(self, e):
        self.opened = False
        self.gd.content = self.kb_close
        self.gd.left = None
        self.gd.top = None
        self.gd.right = 10
        self.gd.bottom = 10
        self.gd.update()

    def __on_pan_update(self, e: ft.DragUpdateEvent):
        if self.opened:
            e.control.top = max(0, e.control.top + e.delta_y)
            e.control.left = max(0, e.control.left + e.delta_x)
            e.control.update()

    def __on_key_click(self, e):
        txt = e.control.text
        # 不能以点开头
        if self.words == "" and txt == '.':
            return
        # 只能输入一个点
        if self.type == 'float' and '.' in self.words and txt == '.':
            return
        self.words += txt
        self.__on_change(self.words)

    def __on_delete_one(self, e):
        self.words = self.words[:-1]
        self.__on_change(self.words)

    def __on_delete_all(self, e):
        self.words = ""
        self.__on_change(self.words)

    def __on_change(self, e):
        if self.tf is not None:
            self.tf.value = e
            self.tf.update()


keyboard = Keyboard()
# async def main(page: ft.Page):
#     def on_change(e):
#         tf.value = e
#         tf.update()
#     kb = Keyboard(on_change=on_change)
#     page.overlay.append(kb)
#     tf = ft.TextField(value="123", read_only=True, on_focus=lambda e: kb.open())
#     tf2 = ft.TextField(value="123", read_only=True, on_focus=lambda e: kb.open())
#     page.add(tf)
#     page.add(tf2)
#     page.window.width = 1024
#     page.window.height = 768


# ft.app(main)
