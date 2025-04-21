import flet as ft

from .keyboard import Keyboard

class InputNumber(ft.Container):
    def __init__(self):
        super().__init__()
        self.keyboard = Keyboard(on_change=self.__on_change)
        self.on_tap_down = self.__on_tap_down

    def __on_change(self, words: str):
        self.content.value = words
        self.content.update()

    def __on_tap_down(self, e: ft.ContainerTapEvent):
        e.page.overlay.clear()

        self.kb.set_position(e.global_x, e.global_y)

        e.page.overlay.append(self.kb)
        e.page.update()

    def __on_click(self, e):
        self.content.border_color = ft.Colors.PRIMARY

    def build(self):
        self.content: ft.TextField = ft.TextField(value="", read_only=True, on_click=self.__on_click)


async def main(page: ft.Page):
    # def on_focus(e):
    #     page.overlay.clear()
    #     kb = Keyboard()
    #     page.overlay.append(kb)
    #     page.update()
    #     kb.visible = True
    #     kb.update()

    # page.add(ft.TextField(value="456", on_focus=on_focus))
    # page.add(ft.TextField(value="123", on_focus=on_focus))

    page.add(InputNumber())
    page.add(InputNumber())
    page.add(InputNumber())
    page.add(InputNumber())

ft.app(main)
