import flet as ft


class Keyboard(ft.Stack):
    def __init__(self, on_change: ft.OptionalEventCallable):
        super().__init__()
        self.words = ""
        self.__on_change = on_change
        self.__x = 0
        self.__y = 0

    def build(self):
        number_keys = [ft.OutlinedButton(str(i), col={"xs": 4}, on_click=self.__on_key_click) for i in range(1, 10)]
        number_keys.append(ft.OutlinedButton(str(0), col={"xs": 4}, on_click=self.__on_key_click))
        number_keys.append(ft.OutlinedButton('.', col={"xs": 4}, on_click=self.__on_key_click))
        number_keys.append(ft.OutlinedButton(icon=ft.Icons.BACKSPACE_OUTLINED, col={"xs": 4}, on_click=self.__on_key_delete))

        kb_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(content=ft.Text("Dragable Keyboard", weight=ft.FontWeight.BOLD), padding=ft.padding.only(left=10)),
                ft.IconButton(icon=ft.Icons.CLOSE, on_click=self.on_close)
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
        self.kb_container = ft.Container(
            expand=False,
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

        self.controls = [
            ft.GestureDetector(
                left=self.__x,
                top=self.__y + 40,
                mouse_cursor=ft.MouseCursor.MOVE,
                drag_interval=10,
                on_pan_update=self.__on_pan_update,
                content=self.kb_container
            )
        ]

    def on_close(self, e):
        if self.words.endswith("."):
            self.words = self.words[:-1]
        self.__on_change(self.words)
        e.page.overlay.remove(self)
        e.page.update()

        # 设置所有的边框的默认颜色
        for control in e.page.controls:
            if isinstance(control, InputNumber):
                control.content.border_color = ft.Colors.BLACK
                control.content.update()

    def __on_pan_update(self, e: ft.DragUpdateEvent):
        e.control.top = max(0, e.control.top + e.delta_y)
        e.control.left = max(0, e.control.left + e.delta_x)
        e.control.update()

    def __on_key_click(self, e):
        txt = e.control.text
        # 不能以点开头
        if self.words == "" and txt == '.':
            return
        # 只能输入一个点
        if '.' in self.words and txt == '.':
            return
        self.words += txt
        self.__on_change(self.words)

    def __on_key_delete(self, e):
        self.words = self.words[:-1]
        self.__on_change(self.words)

    def set_position(self, x: int, y: int):
        self.__x = x
        self.__y = y
        print(self.__x, self.__y)


class InputNumber(ft.Container):
    def __init__(self):
        super().__init__()
        self.kb = Keyboard(on_change=self.__on_change)
        self.on_tap_down = self.__on_tap_down

    def __on_change(self, words: str):
        self.content.value = words
        self.content.update()

    def __on_tap_down(self, e: ft.ContainerTapEvent):
        # 把别人的移除掉
        for kb in e.page.overlay:
            if isinstance(kb, Keyboard):
                kb.on_close(e)

        # 设置别人的边框的默认颜色
        for control in e.page.controls:
            if isinstance(control, InputNumber):
                control.content.border_color = ft.Colors.BLACK
                control.content.update()

        # 设置自己的边框的激活颜色
        self.content.border_color = ft.Colors.PRIMARY
        self.content.update()

        self.kb.set_position(e.global_x, e.global_y)
        # 添加自己的
        e.page.overlay.append(self.kb)
        e.page.update()

    def build(self):
        self.content: ft.TextField = ft.TextField(key="input_number", value="", read_only=True)


async def main(page: ft.Page):
    page.add(InputNumber())
    page.add(InputNumber())
    page.add(InputNumber())
    page.add(InputNumber())

ft.app(main)