import os
import flet as ft
from pathlib import Path
from db.models.event_log import EventLog
from db.models.user import User
from ui.common.permission_check import PermissionCheck
from task.utc_timer_task import gdata


class AudioAlarm(ft.Container):
    def __init__(self):
        super().__init__()
        self.right = 10
        self.top = 4

    def build(self):
        # create audio alarm
        audit_src = os.path.join(
            Path(__file__).parent.parent.parent,
            "assets",
            "TF001.WAV"
        )
        self.content: ft.FilledButton = ft.FilledButton(
            text="Override",
            icon=ft.Icons.NOTIFICATIONS_ON_OUTLINED,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED,
            visible=False,
            color=ft.Colors.WHITE,
            on_click=self.__on_override_button_click
        )

        self.audio_alarm = ft.Audio(
            src=audit_src,
            autoplay=False,
            release_mode=ft.audio.ReleaseMode.LOOP
        )
        self.page.overlay.append(self.audio_alarm)

    def __on_override_button_click(self, e):
        self.page.open(PermissionCheck(self.__on_mute, 1))

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

    def __on_mute(self, user: User):
        self.audio_alarm.pause()
        self.content.icon = ft.Icons.NOTIFICATIONS_OFF_OUTLINED
        self.content.disabled = True
        self.content.bgcolor = ft.Colors.RED_400
        event_log: EventLog = EventLog.select().order_by(EventLog.id.desc()).first()
        if event_log:
            event_log.acknowledged_at = gdata.utc_date_time
            event_log.save()
        self.content.update()

    def handle_change(self, topic, value):
        if value:
            self.play()
        else:
            self.stop()
