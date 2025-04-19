import asyncio
import flet as ft
from common.const_pubsub_topic import PubSubTopic
from common.global_data import gdata


class FullscreenAlert(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.visible = False
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

    def start(self):
        self.task = self.page.run_task(self.blink)
        self.visible = True
        self.update()

    def stop(self):
        if self.task:
            self.task.cancel()
        self.visible = False
        self.update()

    async def blink(self):
        while True:
            await asyncio.sleep(1)
            self.visible = not self.visible
            self.update()

    def handle_change(self, topic, value):
        if value:
            self.start()
        else:
            self.stop()

    def did_mount(self):
        self.page.pubsub.subscribe_topic(
            PubSubTopic.BREACH_EEXI_OCCURED_FOR_FULLSCREEN,
            self.handle_change
        )

    def will_unmount(self):
        self.page.pubsub.unsubscribe_topic(
            PubSubTopic.BREACH_EEXI_OCCURED_FOR_FULLSCREEN
        )
