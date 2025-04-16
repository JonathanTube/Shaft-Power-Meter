import asyncio
import flet as ft


class FullscreenAlert(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.task = None

    def build_blur_border(self):
        return ft.BoxShadow(
            spread_radius=10,
            blur_radius=10,
            color=ft.Colors.RED,
            offset=ft.Offset(0, 0)
        )

    def build(self):
        left_border = ft.Container(
            left=0,
            top=0,
            bottom=0,
            expand=True,
            shadow=self.build_blur_border()
        )
        top_border = ft.Container(
            left=0,
            right=0,
            top=0,
            shadow=self.build_blur_border()
        )
        right_border = ft.Container(
            right=0,
            top=0,
            bottom=0,
            shadow=self.build_blur_border()
        )
        bottom_border = ft.Container(
            left=0,
            right=0,
            bottom=0,
            shadow=self.build_blur_border()
        )
        self.content = ft.Stack(
            expand=True,
            controls=[
                left_border,
                top_border,
                right_border,
                bottom_border
            ]
        )

    def did_mount(self):
        self.task = self.page.run_task(self.blink)

    async def blink(self):
        while True:
            print("blink")
            print(self.visible)
            await asyncio.sleep(1)
            self.visible = not self.visible
            self.update()

    def will_mount(self):
        self.cancel_task()

    def cancel_task(self):
        if self.task:
            self.task.cancel()

# async def main(page: ft.Page):
#     page.add(FullscreenAlert())

# ft.app(main)
