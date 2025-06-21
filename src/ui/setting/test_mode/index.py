import asyncio
import logging
import flet as ft

from ui.common.permission_check import PermissionCheck
from ui.setting.test_mode.test_mode_instant import TestModeInstant
from ui.setting.test_mode.test_mode_range import TestModeRange
from utils.plc_util import plc_util
from utils.unit_converter import UnitConverter
from db.models.preference import Preference
from task.test_mode_task import testModeTask
from ui.common.toast import Toast
from common.control_manager import ControlManager
from common.global_data import gdata
from db.models.operation_log import OperationLog
from common.operation_type import OperationType
from db.models.user import User
from ui.common.windows_sound_player import WindowsSoundPlayer


class TestMode(ft.Container):
    def __init__(self):
        super().__init__()
        self.alignment = ft.alignment.center
        self.running = testModeTask.is_running
        self.preference: Preference = Preference.get()

        self.sound_testing = False

        self.player = WindowsSoundPlayer()

        self.last_op_utc_date_time = gdata.utc_date_time

        self.op_user = None

    def build(self):
        self.content = ft.TextButton(
            icon=ft.Icons.LOCK_ROUNDED,
            text="",
            style=ft.ButtonStyle(
                icon_size=100,
                icon_color=ft.Colors.INVERSE_SURFACE
            ),
            on_click=lambda e : self.page.open(self.permission_check)
        )
        self.permission_check = PermissionCheck(on_confirm=self.create_controls, user_role=0)

    def create_controls(self, user: User):
        self.op_user = user
        if not self.page:
            return

        self.alignment = ft.alignment.top_left

        s = self.page.session
        self.dlg_stop_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(s.get("lang.setting.test_mode.please_confirm")),
            content=None,
            actions=[
                ft.TextButton(s.get("lang.button.confirm"), on_click=lambda e: self.stop_test_mode),
                ft.TextButton(s.get("lang.button.cancel"), on_click=lambda e: e.page.close(self.dlg_stop_modal))
            ]
        )

        self.range_card = TestModeRange()
        self.instant_card = TestModeInstant()

        self.start_button = ft.FilledButton(
            height=40,
            text=self.page.session.get('lang.button.start_test_mode'),
            bgcolor=ft.Colors.GREEN,
            visible=not self.running,
            color=ft.Colors.WHITE,
            icon=ft.Icons.PLAY_ARROW_OUTLINED,
            icon_color=ft.Colors.WHITE,
            on_click=self.start_test_mode
        )

        self.stop_button = ft.FilledButton(
            height=40,
            text=self.page.session.get('lang.button.stop_test_mode'),
            bgcolor=ft.Colors.RED,
            visible=self.running,
            color=ft.Colors.WHITE,
            icon=ft.Icons.TERMINAL_OUTLINED,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: e.page.open(self.dlg_stop_modal)
        )

        self.auto_test_button = ft.FilledButton(
            height=40,
            text=self.page.session.get('lang.button.stop_fatigue_testing') if gdata.auto_testing else self.page.session.get('lang.button.start_fatigue_testing'),
            bgcolor=ft.Colors.RED if gdata.auto_testing else ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            icon=ft.Icons.AUTO_MODE_OUTLINED,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: self.__on_toggle_auto_test()
        )

        self.sound_test_button = ft.FilledButton(
            height=40,
            text=self.page.session.get('lang.button.start_sound_testing'),
            icon=ft.Icons.AUDIOTRACK_OUTLINED,
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: self.__on_toggle_sound_test()
        )

        self.content = ft.Column(
            controls=[
                self.range_card,
                self.instant_card,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[self.start_button, self.stop_button, self.auto_test_button, self.sound_test_button]
                )
            ]
        )
        self.update()

    def __on_toggle_sound_test(self):
        if self.sound_testing:
            self.sound_test_button.text = self.page.session.get('lang.button.start_sound_testing')
            self.sound_test_button.bgcolor = ft.Colors.GREEN
            self.player.stop()
        else:
            self.sound_test_button.text = self.page.session.get('lang.button.stop_sound_testing')
            self.sound_test_button.bgcolor = ft.Colors.RED
            self.player.play()
        self.sound_testing = not self.sound_testing
        self.sound_test_button.update()

    def __on_toggle_auto_test(self):
        if gdata.auto_testing:
            self.auto_test_button.bgcolor = ft.Colors.GREEN
            self.auto_test_button.text = self.page.session.get('lang.button.start_fatigue_testing')
        else:
            self.auto_test_button.bgcolor = ft.Colors.RED
            self.auto_test_button.text = self.page.session.get('lang.button.stop_fatigue_testing')

        self.auto_test_button.update()
        gdata.auto_testing = not gdata.auto_testing

    def convert_torque(self, torque):
        value = float(torque)
        if self.preference.system_unit == 0:
            return float(value * 1000)
        else:
            return UnitConverter.tm_to_nm(value)

    def convert_thrust(self, thrust):
        value = float(thrust)
        if self.preference.system_unit == 0:
            return float(value * 1000)
        else:
            return UnitConverter.t_to_n(value)

    def start_test_mode(self, e):
        if self.running:
            return

        self.page.run_task(testModeTask.start)

        self.running = True
        gdata.test_mode_running = True
        self.range_card.enable()

        self.start_button.visible = False
        self.start_button.update()
        self.stop_button.visible = True
        self.stop_button.update()

        OperationLog.create(
            user_id=self.op_user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.TEST_MODE_CONF,
            operation_content='started test mode'
        )
        Toast.show_success(self.page)
        # 将sps设备设置为在线，防止offline_task 写入默认值
        gdata.sps1_offline = False
        gdata.sps2_offline = False

    def stop_test_mode(self, e):
        if not self.running:
            return

        gdata.test_mode_running = False
        self.range_card.disable()

        testModeTask.stop()
        self.page.close(self.dlg_stop_modal)
        self.running = False
        self.start_button.visible = True
        self.start_button.update()
        self.stop_button.visible = False
        self.stop_button.update()
        # 恢复现场
        gdata.sps1_offline = True
        gdata.sps2_offline = True

        OperationLog.create(
            user_id=self.op_user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.TEST_MODE_CONF,
            operation_content='stopped test mode'
        )

        ControlManager.audio_alarm.stop()
        ControlManager.fullscreen_alert.stop()
        self.page.run_task(plc_util.write_alarm, False)
        self.page.run_task(plc_util.write_power_overload, False)
        Toast.show_success(self.page)

    async def __auto_lock(self):
        while self.task_running:
            if self.visible:
                try:
                    time_diff = gdata.utc_date_time - self.last_op_utc_date_time
                    # print(time_diff.total_seconds())
                    if time_diff.total_seconds() > 60 * 10:
                        self.visible = False
                        self.page.open(self.permission_check)
                        self.update()
                except Exception as e:
                    logging.exception(e)
            await asyncio.sleep(1)

    def did_mount(self):
        self.task_running = True
        if not gdata.auto_testing:
            self.page.open(self.permission_check)
        self.task = self.page.run_task(self.__auto_lock)

    def will_unmount(self):
        self.task_running = False
        self.player.stop()
        if self.task is not None:
            self.task.cancel()
