import asyncio
import logging
import flet as ft


class FullscreenAlert(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.visible = False
        self.task = None
        self.running = False
        self.content = self._create_border_stack()

    def _create_border_stack(self):
        border_shadow = ft.BoxShadow(
            spread_radius=10,
            blur_radius=10,
            color=ft.Colors.RED,
            offset=ft.Offset(0, 0)
        )
        return ft.Stack(
            expand=True,
            controls=[
                ft.Container(left=0, top=0, bottom=0, expand=True, shadow=border_shadow),
                ft.Container(left=0, right=0, top=0, shadow=border_shadow),
                ft.Container(right=0, top=0, bottom=0, shadow=border_shadow),
                ft.Container(left=0, right=0, bottom=0, shadow=border_shadow)
            ]
        )

    def show(self):
        if not self.running:
            self.running = True
            if self.page is not None:
                self.task = self.page.run_task(self._blink)

    def hide(self):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
            self.visible = False
            if self.page:
                self.update()

    async def _blink(self):
        try:
            while self.running:
                await asyncio.sleep(1)
                self.visible = not self.visible
                if self.page:
                    self.update()
        except asyncio.CancelledError:
            pass
        except Exception:
            logging.exception("Exception in FullscreenAlert._blink")
        finally:
            self.visible = False
            if self.page:
                self.update()