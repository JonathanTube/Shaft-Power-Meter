import logging
import flet as ft
from db.models.user import User
from db.models.event_log import EventLog
from ui.common.permission_check import PermissionCheck
from task.utc_timer_task import gdata
from task.plc_sync_task import plc
from websocket.websocket_slave import ws_client


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
                on_click=lambda e: self.page.open(
                    PermissionCheck(self.on_mute, 1))
            )
        except:
            logging.exception('exception occured at AudioAlarm.build')

    def show(self):
        try:
            # 向plc发送报警-打开
            self.notify_eexi_breach(True)
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
            # 向plc发送报警-关闭
            self.notify_eexi_breach(False)
            if self.content and self.content.page:
                self.content.visible = False
                self.content.update()
        except:
            logging.exception('exception occured at AudioAlarm.hide')

    def on_mute(self, user: User):
        try:
            # 向plc发送报警-关闭
            self.notify_eexi_breach(False)
            event_log: EventLog = EventLog.select().order_by(EventLog.id.desc()).first()
            if event_log:
                event_log.acknowledged_at = gdata.configDateTime.utc_date_time
                event_log.save()

            if self.content and self.content.page:
                self.content.icon = ft.Icons.NOTIFICATIONS_OFF_OUTLINED
                self.content.disabled = True
                self.content.bgcolor = ft.Colors.RED_400
                self.content.update()
        except:
            logging.exception('exception occured at AudioAlarm.on_mute')

    def notify_eexi_breach(self, occured):
        if gdata.configCommon.is_master:
            # write_eexi_breach_alarm内部会判断是否连接plc
            self.page.run_task(plc.write_eexi_breach_alarm, occured)
        else:
            self.page.run_task(ws_client.send_eexi_breach_alarm_to_master, occured)
