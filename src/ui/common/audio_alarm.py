import os
import flet as ft
from pathlib import Path
from common.const_pubsub_topic import PubSubTopic


class AudioAlarm(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.right = 10
        self.top = 4

    def build(self):
        # create audio alarm
        audit_src = os.path.join(
            Path(__file__).parent.parent.parent,
            "assets",
            "alarm.mp3"
        )
        self.content: ft.FilledButton = ft.FilledButton(
            text="Override",
            icon=ft.Icons.NOTIFICATIONS_ON_OUTLINED,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED,
            visible=False,
            color=ft.Colors.WHITE,
            on_click=self.__on_mute
        )

        self.audio_alarm = ft.Audio(
            src=audit_src,
            autoplay=False,
            release_mode=ft.audio.ReleaseMode.LOOP
        )
        self.page.overlay.append(self.audio_alarm)

    def play(self):
        self.audio_alarm.play()
        self.content.visible = True
        self.content.disabled = False
        self.content.icon = ft.Icons.NOTIFICATIONS_ON_OUTLINED
        self.content.bgcolor = ft.Colors.RED
        self.content.update()

    def stop(self):
        self.audio_alarm.pause()
        self.content.visible = False
        self.content.update()

    def __on_mute(self, e: ft.ControlEvent):
        self.audio_alarm.pause()
        self.content.icon = ft.Icons.NOTIFICATIONS_OFF_OUTLINED
        self.content.disabled = True
        self.content.bgcolor = ft.Colors.RED_400
        self.content.update()

    def handle_change(self, topic, value):
        if value:
            self.play()
        else:
            self.stop()

    def did_mount(self):
        self.page.pubsub.subscribe_topic(
            PubSubTopic.BREACH_EEXI_OCCURED_FOR_AUDIO,
            self.handle_change
        )

    def will_unmount(self):
        self.page.pubsub.unsubscribe_topic(
            PubSubTopic.BREACH_EEXI_OCCURED_FOR_AUDIO
        )
