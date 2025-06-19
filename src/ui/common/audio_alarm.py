import flet as ft
from db.models.event_log import EventLog
from db.models.user import User
from ui.common.permission_check import PermissionCheck
from task.utc_timer_task import gdata


class AudioAlarm(ft.Container):
    def __init__(self,audio : ft.Audio):
        super().__init__()
        self.right = 10
        self.top = 4
        self.audio = audio

    def build(self):
        self.content: ft.FilledButton = ft.FilledButton(
            text="Override",
            icon=ft.Icons.NOTIFICATIONS_ON_OUTLINED,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED,
            visible=False,
            color=ft.Colors.WHITE,
            on_click=self.__on_override_button_click
        )       

    def __on_override_button_click(self, e):
        self.page.open(PermissionCheck(self.__on_mute, 1))

    def play(self):
        self.audio.play()
        self.content.visible = True
        self.content.disabled = False
        self.content.icon = ft.Icons.NOTIFICATIONS_ON_OUTLINED
        self.content.bgcolor = ft.Colors.RED
        self.content.update()

    def stop(self):
        self.audio.pause()
        self.content.visible = False
        self.content.update()

    def __on_mute(self, user: User):
        self.audio.pause()
        self.content.icon = ft.Icons.NOTIFICATIONS_OFF_OUTLINED
        self.content.disabled = True
        self.content.bgcolor = ft.Colors.RED_400
        event_log: EventLog = EventLog.select().order_by(EventLog.id.desc()).first()
        if event_log:
            event_log.acknowledged_at = gdata.utc_date_time
            event_log.save()
        self.content.update()