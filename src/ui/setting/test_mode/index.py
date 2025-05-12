import flet as ft

from ui.setting.test_mode.test_mode_instant import TestModeInstant
from ui.setting.test_mode.test_mode_range import TestModeRange
from utils.plc_util import plc_util
from utils.unit_converter import UnitConverter
from db.models.preference import Preference
from task.test_mode_task import testModeTask
from ui.common.toast import Toast
from ui.common.permission_check import PermissionCheck
from common.control_manager import ControlManager
from common.global_data import gdata
from db.models.opearation_log import OperationLog
from common.operation_type import OperationType
from db.models.user import User


class TestMode(ft.Container):
    def __init__(self):
        super().__init__()
        self.alignment = ft.alignment.top_left
        self.running = testModeTask.is_running
        self.preference: Preference = Preference.get()

    def __on_start_button_click(self, e):
        try:
            self.page.open(PermissionCheck(self.start_test_mode, 0))
        except Exception as e:
            pass

    def __on_stop_button_click(self, e):
        try:
            self.page.open(PermissionCheck(self.stop_test_mode, 0))
        except Exception as e:
            pass

    def build(self):
        s = self.page.session
        self.dlg_stop_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(s.get("lang.setting.test_mode.please_confirm")),
            content=None,
            actions=[
                ft.TextButton(s.get("lang.button.confirm"), on_click=lambda e: self.__on_stop_button_click(e)),
                ft.TextButton(s.get("lang.button.cancel"), on_click=lambda e: e.page.close(self.dlg_stop_modal))
            ]
        )

        self.range_card = TestModeRange()
        self.instant_card = TestModeInstant()

        self.start_button = ft.FilledButton(
            width=120,
            height=40,
            text=self.page.session.get('lang.button.start'),
            bgcolor=ft.Colors.GREEN,
            visible=not self.running,
            on_click=lambda e: self.__on_start_button_click(e)
        )

        self.stop_button = ft.FilledButton(
            width=120,
            height=40,
            text=self.page.session.get('lang.button.stop'),
            bgcolor=ft.Colors.RED,
            visible=self.running,
            on_click=lambda e: e.page.open(self.dlg_stop_modal)
        )

        self.content = ft.Column(
            controls=[
                self.range_card,
                self.instant_card,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[self.start_button, self.stop_button]
                )
            ]
        )

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

    def start_test_mode(self, user: User):
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
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.TEST_MODE_CONF,
            operation_content='started test mode'
        )
        Toast.show_success(self.page)

    def stop_test_mode(self, user: User):
        if not self.running:
            return

        self.range_card.disable()

        testModeTask.stop()
        self.page.close(self.dlg_stop_modal)
        self.running = False
        self.start_button.visible = True
        self.start_button.update()
        self.stop_button.visible = False
        self.stop_button.update()

        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.TEST_MODE_CONF,
            operation_content='stopped test mode'
        )

        ControlManager.audio_alarm.stop()
        ControlManager.fullscreen_alert.stop()
        self.page.run_task(plc_util.write_alarm, False)
        self.page.run_task(plc_util.write_power_overload, False)
        Toast.show_success(self.page)
