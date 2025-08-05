import logging
import flet as ft
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
        try:
            self.content: ft.FilledButton = ft.FilledButton(
                text="Override",
                icon=ft.Icons.NOTIFICATIONS_ON_OUTLINED,
                icon_color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED,
                visible=False,
                color=ft.Colors.WHITE,
                on_click=lambda e: self.page.open(PermissionCheck(self.on_mute, 1))
            )
        except:
            logging.exception('exception occured at AudioAlarm.build')


    def show(self):
        try:
            if self.content and self.content.page:
                self.content.visible = True
                self.content.disabled = False
                self.content.icon = ft.Icons.NOTIFICATIONS_ON_OUTLINED
                self.content.bgcolor = ft.Colors.RED
                self.content.update()
        except:
            logging.exception('exception occured at AudioAlarm.show')

    def hide(self):
        try:
            if self.content and self.content.page:
                self.content.visible = False
                self.content.update()
        except:
            logging.exception('exception occured at AudioAlarm.hide')

    def on_mute(self, user: User):
        try:
            event_log: EventLog = EventLog.select().order_by(EventLog.id.desc()).first()
            if event_log:
                event_log.acknowledged_at = gdata.utc_date_time
                event_log.save()

            if self.content and self.content.page:
                self.content.icon = ft.Icons.NOTIFICATIONS_OFF_OUTLINED
                self.content.disabled = True
                self.content.bgcolor = ft.Colors.RED_400
                self.content.update()
        except:
            logging.exception('exception occured at AudioAlarm.on_mute')
