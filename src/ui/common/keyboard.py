import logging
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
        self.gd = None
        self.kb_open = None
        self.kb_close = None
        self.point = None

    def build(self):
        try:
            # 数字按键
            number_keys = [ft.OutlinedButton(str(i), col={"xs": 4}, on_click=self._on_key_click) for i in range(1, 10)]
            number_keys.append(ft.OutlinedButton(str(0), col={"xs": 4}, on_click=self._on_key_click))

            # 小数点
            self.point = ft.OutlinedButton('.', col={"xs": 4}, on_click=self._on_key_click)
            number_keys.append(self.point)

            # 删除按钮
            number_keys.append(ft.OutlinedButton(
                icon=ft.Icons.BACKSPACE_OUTLINED, col={"xs": 4},
                on_click=self._on_delete_one, on_long_press=self._on_delete_all
            ))

            kb_header = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Container(content=ft.Icon(ft.Icons.KEYBOARD_OUTLINED, size=30), padding=ft.padding.only(left=10)),
                    ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, on_click=self._on_close)
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

            self.kb_close = ft.IconButton(icon=ft.Icons.KEYBOARD_OUTLINED, on_click=self._on_open)

            self.gd = ft.GestureDetector(
                right=10,
                bottom=10,
                expand=False,
                mouse_cursor=ft.MouseCursor.MOVE,
                drag_interval=10,
                on_pan_update=self._on_pan_update,
                content=self.kb_close
            )

            self.controls = [self.gd]
        except:
            logging.exception('【键盘】构建界面时发生异常')

    def show(self):
        try:
            if self.page:
                self.visible = True
                self.update()
        except:
            logging.exception("【键盘】显示时发生异常")

    def open(self, text_field: ft.TextField, type: Literal['int', 'float', 'ip'] = 'float'):
        if self.page:
            self.show()
            try:
                # 恢复上一个输入框的边框颜色
                if self.tf and self.tf.page:
                    self.tf.border_color = ft.Colors.BLACK
                    self.tf.update()

                if text_field is not None:
                    self.words = str(text_field.value)

                if not self.opened:
                    self._on_open(None)

                self.type = type
                if self.point and self.point.page:
                    self.point.visible = self.type in ('float', 'ip')
                    self.point.update()

                self.tf = text_field
                # 高亮当前输入框
                if self.tf and self.tf.page:
                    self.tf.border_color = ft.Colors.PRIMARY
                    self.tf.update()
            except:
                logging.exception("【键盘】打开时发生异常")

    def close(self):
        try:
            self.visible = False
            self.update()
            self._on_close(None)
        except:
            logging.exception("【键盘】关闭时发生异常")

    def _on_open(self, e):
        try:
            self.opened = True
            if self.gd and self.gd.page:
                self.gd.content = self.kb_open
                self.gd.left = 500
                self.gd.top = 250
                self.gd.right = None
                self.gd.bottom = None
                self.gd.update()
        except:
            logging.exception("【键盘】打开面板时发生异常")

    def _on_close(self, e):
        try:
            self.opened = False
            if self.gd and self.gd.page:
                self.gd.content = self.kb_close
                self.gd.left = None
                self.gd.top = None
                self.gd.right = 10
                self.gd.bottom = 10
                self.gd.update()
        except:
            logging.exception("【键盘】关闭面板时发生异常")

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        try:
            if self.opened and e.control is not None:
                e.control.top = max(0, e.control.top + e.delta_y)
                e.control.left = max(0, e.control.left + e.delta_x)
                e.control.update()
        except:
            logging.exception("【键盘】拖动位置时发生异常")

    def _on_key_click(self, e):
        try:
            if e.control is not None:
                txt = e.control.text
                if self.words == "" and txt == '.':
                    return
                if self.type == 'float' and '.' in self.words and txt == '.':
                    return
                self.words += txt
                self._on_change(self.words)
        except:
            logging.exception("【键盘】点击按键时发生异常")

    def _on_delete_one(self, e):
        try:
            self.words = self.words[:-1]
            self._on_change(self.words)
        except:
            logging.exception("【键盘】删除一个字符时发生异常")

    def _on_delete_all(self, e):
        try:
            self.words = ""
            self._on_change(self.words)
        except:
            logging.exception("【键盘】清空输入时发生异常")

    def _on_change(self, value: str):
        try:
            if self.tf and self.tf.page:
                self.tf.value = value
                self.tf.update()
        except:
            logging.exception("【键盘】更新输入值时发生异常")


keyboard = Keyboard()
