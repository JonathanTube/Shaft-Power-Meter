import asyncio
import logging
import flet as ft

from ui.common.permission_check import PermissionCheck
from ui.setting.test_mode.test_mode_instant import TestModeInstant
from ui.setting.test_mode.test_mode_range import TestModeRange
from task.plc_sync_task import plc
from utils.unit_converter import UnitConverter
from db.models.preference import Preference
from task.test_mode_task import test_mode_task
from ui.common.toast import Toast
from common.global_data import gdata
from db.models.user import User


class TestMode(ft.Container):
    def __init__(self):
        super().__init__()
        self.running = test_mode_task.is_running
        self.preference: Preference = Preference.get()

        self.last_op_utc_date_time = gdata.configDateTime.utc

        self.op_user = None

    def build(self):
        try:
            if self.page and self.page.session:
                self.__create_lock_button()
                self.permission_check = PermissionCheck(on_confirm=self.create_controls, user_role=0)
        except:
            logging.exception('exception occured at TestMode.build')

    def __create_lock_button(self):
        try:
            self.alignment = ft.alignment.center
            self.content = ft.TextButton(
                icon=ft.Icons.LOCK_ROUNDED,
                text="",
                style=ft.ButtonStyle(
                    icon_size=100,
                    icon_color=ft.Colors.INVERSE_SURFACE
                ),
                on_click=lambda e: self.page.open(self.permission_check)
            )
        except:
            pass

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
                ft.TextButton(s.get("lang.button.confirm"), on_click=self.stop_test_mode),
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
            text=self.page.session.get('lang.button.stop_fatigue_testing') if gdata.configTest.auto_testing else self.page.session.get('lang.button.start_fatigue_testing'),
            bgcolor=ft.Colors.RED if gdata.configTest.auto_testing else ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            icon=ft.Icons.AUTO_MODE_OUTLINED,
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: self.__on_toggle_auto_test()
        )

        self.content = ft.Column(
            controls=[
                self.range_card,
                self.instant_card,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[self.start_button, self.stop_button, self.auto_test_button]
                )
            ]
        )
        self.update()

    def __on_toggle_auto_test(self):
        try:
            if self.auto_test_button and self.auto_test_button.page:
                if gdata.configTest.auto_testing:
                    self.auto_test_button.bgcolor = ft.Colors.GREEN
                    self.auto_test_button.text = self.page.session.get('lang.button.start_fatigue_testing')
                else:
                    self.auto_test_button.bgcolor = ft.Colors.RED
                    self.auto_test_button.text = self.page.session.get('lang.button.stop_fatigue_testing')

                self.auto_test_button.update()
                gdata.configTest.auto_testing = not gdata.configTest.auto_testing
        except:
            Toast.show_error(self.page, "__on_toggle_auto_test failed.")

    def convert_torque(self, torque: int):
        if self.preference.system_unit == 0:
            return torque * 1000
        else:
            return UnitConverter.tm_to_nm(torque)

    def convert_thrust(self, thrust: int):
        if self.preference.system_unit == 0:
            return thrust * 1000
        else:
            return UnitConverter.t_to_n(thrust)

    def start_test_mode(self, e):
        try:
            if self.running:
                return

            self.page.run_task(test_mode_task.start)

            self.range_card.enable()

            if self.start_button and self.start_button.page:
                self.start_button.visible = False
                self.start_button.update()

            if self.stop_button and self.stop_button:
                self.stop_button.visible = True
                self.stop_button.update()

            self.running = True
            gdata.configTest.test_mode_running = True
            Toast.show_success(self.page)
        except:
            Toast.show_error(self.page, "start test mode failed.")

    def stop_test_mode(self, e):
        try:
            if not self.running:
                return

            self.page.run_task(test_mode_task.stop)
            self.range_card.disable()
            self.page.close(self.dlg_stop_modal)
            self.running = False
            if self.start_button and self.start_button.page:
                self.start_button.visible = True
                self.start_button.update()

            if self.stop_button and self.stop_button.page:
                self.stop_button.visible = False
                self.stop_button.update()

            # 恢复现场
            gdata.configTest.test_mode_running = False
            gdata.configCommon.is_eexi_breaching = False
            gdata.configSPS.speed = 0.0
            gdata.configSPS.power = 0
            gdata.configSPS.torque = 0
            gdata.configSPS.thrust = 0
            gdata.configSPS.ad0 = 0
            gdata.configSPS.ad1 = 0

            gdata.configSPS2.speed = 0.0
            gdata.configSPS2.power = 0
            gdata.configSPS2.torque = 0
            gdata.configSPS2.thrust = 0
            gdata.configSPS2.ad0 = 0
            gdata.configSPS2.ad1 = 0
            # 这里只需要回复power_overload的告警，alarm不需要管。
            self.page.run_task(plc.write_power_overload, False)
            Toast.show_success(self.page)
        except:
            Toast.show_error(self.page, "stop test mode failed.")

    async def __auto_lock(self):
        while self.task_running:
            try:
                time_diff = gdata.configDateTime.utc - self.last_op_utc_date_time
                if time_diff.total_seconds() > 60 * 10:
                    self.__create_lock_button()
                    if self.page:
                        self.update()
            except:
                return
            await asyncio.sleep(1)

    def did_mount(self):
        self.task_running = True
        if not gdata.configTest.auto_testing:
            self.page.open(self.permission_check)
        self.task = self.page.run_task(self.__auto_lock)

    def will_unmount(self):
        self.task_running = False

        if self.task is not None:
            self.task.cancel()
