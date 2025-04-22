import flet as ft

from db.models.test_mode_conf import TestModeConf
from ui.setting.test_mode.test_mode_instant import TestModeInstant
from ui.setting.test_mode.test_mode_range import TestModeRange
from utils.unit_converter import UnitConverter
from db.models.preference import Preference
from task.test_mode_task import testModeTask
from ui.common.toast import Toast
from ui.common.permission_check import PermissionCheck
from common.control_manager import ControlManager


class TestMode(ft.Container):
    def __init__(self):
        super().__init__()
        self.alignment = ft.alignment.top_left
        self.running = testModeTask.is_running
        self.preference: Preference = Preference.get()

    def __on_start_button_click(self, e):
        self.page.open(PermissionCheck(self.start_test_mode, 0))

    def build(self):
        s = self.page.session
        self.dlg_stop_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(s.get("lang.setting.test_mode.please_confirm")),
            content=None,
            actions=[
                ft.TextButton(s.get("lang.button.confirm"), on_click=lambda e: self.stop_test_mode(e)),
                ft.TextButton(s.get("lang.button.cancel"), on_click=lambda e: e.page.close(self.dlg_stop_modal))
            ]
        )

        self.range_card = TestModeRange()
        self.instant_card = TestModeInstant()

        self.save_button = ft.FilledButton(
            width=120,
            height=40,
            text=self.page.session.get('lang.button.save'),
            bgcolor=ft.Colors.PRIMARY,
            visible=not self.running,
            on_click=lambda e: self.__on_save_button_click(e)
        )

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
                    controls=[self.save_button, self.start_button, self.stop_button]
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

    def __on_save_button_click(self, e):
        self.page.open(PermissionCheck(self.range_card.save_data, 0))

    def start_test_mode(self):
        if self.running:
            return

        try:
            conf: TestModeConf = TestModeConf.get()
            min_torque = self.convert_torque(conf.min_torque)
            max_torque = self.convert_torque(conf.max_torque)
            testModeTask.set_torque_range(min_torque, max_torque)

            min_speed = int(conf.min_speed)
            max_speed = int(conf.max_speed)
            testModeTask.set_speed_range(min_speed, max_speed)

            min_thrust = self.convert_thrust(conf.min_thrust)
            max_thrust = self.convert_thrust(conf.max_thrust)
            testModeTask.set_thrust_range(min_thrust, max_thrust)

            min_rev = int(conf.min_revolution)
            max_rev = int(conf.max_revolution)
            testModeTask.set_revolution_range(min_rev, max_rev)

            self.page.run_task(testModeTask.start)
            self.running = True
            self.start_button.visible = False
            self.start_button.update()
            self.stop_button.visible = True
            self.stop_button.update()
            self.save_button.visible = False
            self.save_button.update()

            Toast.show_success(self.page)
        except Exception as e:
            print(e)
            Toast.show_error(self.page, str(e))

    def stop_test_mode(self, e):
        if not self.running:
            return

        testModeTask.stop()
        self.page.close(self.dlg_stop_modal)
        self.running = False
        self.start_button.visible = True
        self.start_button.update()
        self.stop_button.visible = False
        self.stop_button.update()
        self.save_button.visible = True
        self.save_button.update()

        ControlManager.on_eexi_power_breach_recovery()
        ControlManager.on_power_overload_recovery()
        Toast.show_success(self.page)
