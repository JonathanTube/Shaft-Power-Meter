import asyncio
import os
import flet as ft

from common.const_pubsub_topic import PubSubTopic
from db.models.system_settings import SystemSettings
from utils.unit_converter import UnitConverter
from utils.unit_parser import UnitParser
from db.models.preference import Preference
from db.models.test_mode_conf import TestModeConf
from task.test_mode_task import TestModeTask
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast
from common.global_data import gdata


class TestMode(ft.Container):
    def __init__(self, test_mode_task: TestModeTask):
        super().__init__()
        self.test_mode_task = test_mode_task
        self.alignment = ft.alignment.top_left
        self.running = self.test_mode_task.is_running
        self.system_settings = SystemSettings.get()
        self.preference = Preference.get()
        self.test_mode_conf = TestModeConf.get()

    def create_stop_dlg(self):
        self.dlg_stop_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please Confirm"),
            content=ft.Text(
                "All of the test data will be deleted. Are you sure you want to stop the test mode?"),
            actions=[
                ft.TextButton(
                    "Confirm", on_click=lambda e: self.stop_test_mode(e)),
                ft.TextButton(
                    "Cancel", on_click=lambda e: e.page.close(self.dlg_stop_modal))
            ]
        )

    def create_start_dlg(self):
        self.dlg_start_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please Confirm"),
            content=ft.Text("Are you sure you want to start the test mode?"),
            actions=[
                ft.TextButton(
                    "Confirm", on_click=lambda e: self.start_test_mode(e)),
                ft.TextButton(
                    "Cancel", on_click=lambda e: e.page.close(self.dlg_start_modal))
            ]
        )

    def get_torque_and_unit(self, value) -> tuple[float, str]:
        system_unit = self.preference.system_unit
        if system_unit == 0:
            return [round(value / 1000, 2), 'kNm']
        else:
            return UnitParser.parse_torque(value, system_unit)

    def get_thrust_and_unit(self, value) -> tuple[float, str]:
        system_unit = self.preference.system_unit
        if system_unit == 0:
            return [round(value / 1000, 2), 'kN']
        else:
            return UnitParser.parse_thrust(value, system_unit)

    def get_uniform_text(self, label):
        return ft.Text(
            value=f"{label}",
            weight=ft.FontWeight.BOLD,
            col={"sm": 12, "md": 6}
        )

    def build(self):
        self.create_stop_dlg()
        self.create_start_dlg()

        min_torque_value, min_torque_unit = self.get_torque_and_unit(
            self.test_mode_conf.min_torque)
        self.min_torque = ft.TextField(
            col={"sm": 12, "md": 6},
            label=self.page.session.get('lang.setting.test_mode.min_torque'),
            suffix_text=min_torque_unit,
            on_click=lambda e: os.system('osk'),
            value=min_torque_value
        )

        max_torque_value, max_torque_unit = self.get_torque_and_unit(
            self.test_mode_conf.max_torque)
        self.max_torque = ft.TextField(
            col={"sm": 12, "md": 6},
            label=self.page.session.get('lang.setting.test_mode.max_torque'),
            suffix_text=max_torque_unit,
            on_click=lambda e: os.system('osk'),
            value=max_torque_value
        )

        self.min_speed = ft.TextField(
            col={"sm": 12, "md": 6},
            label=self.page.session.get('lang.setting.test_mode.min_speed'),
            suffix_text='rpm',
            on_click=lambda e: os.system('osk'),
            value=self.test_mode_conf.min_speed
        )

        self.max_speed = ft.TextField(
            col={"sm": 12, "md": 6},
            label=self.page.session.get('lang.setting.test_mode.max_speed'),
            suffix_text='rpm',
            on_click=lambda e: os.system('osk'),
            value=self.test_mode_conf.max_speed
        )

        min_thrust_value, min_thrust_unit = self.get_thrust_and_unit(
            self.test_mode_conf.min_thrust)
        self.min_thrust = ft.TextField(
            col={"sm": 12, "md": 6},
            label=self.page.session.get('lang.setting.test_mode.min_thrust'),
            suffix_text=min_thrust_unit,
            on_click=lambda e: os.system('osk'),
            value=min_thrust_value
        )

        max_thrust_value, max_thrust_unit = self.get_thrust_and_unit(
            self.test_mode_conf.max_thrust)
        self.max_thrust = ft.TextField(
            col={"sm": 12, "md": 6},
            label=self.page.session.get('lang.setting.test_mode.max_thrust'),
            suffix_text=max_thrust_unit,
            on_click=lambda e: os.system('osk'),
            value=max_thrust_value
        )

        self.min_revolution = ft.TextField(
            col={"sm": 12, "md": 6},
            label=self.page.session.get(
                'lang.setting.test_mode.min_revolution'),
            on_click=lambda e: os.system('osk'),
            value=self.test_mode_conf.min_revolution
        )

        self.max_revolution = ft.TextField(
            col={"sm": 12, "md": 6},
            label=self.page.session.get(
                'lang.setting.test_mode.max_revolution'),
            on_click=lambda e: os.system('osk'),
            value=self.test_mode_conf.max_revolution
        )

        self.save_button = ft.FilledButton(
            width=120,
            height=40,
            text=self.page.session.get('lang.button.save'),
            bgcolor=ft.Colors.PRIMARY,
            visible=not self.running,
            on_click=lambda e: self.save_test_mode_conf(e)
        )

        self.start_button = ft.FilledButton(
            width=120,
            height=40,
            text=self.page.session.get('lang.button.start'),
            bgcolor=ft.Colors.GREEN,
            visible=not self.running,
            on_click=lambda e: e.page.open(self.dlg_start_modal)
        )

        self.stop_button = ft.FilledButton(
            width=120,
            height=40,
            text=self.page.session.get('lang.button.stop'),
            bgcolor=ft.Colors.RED,
            visible=self.running,
            on_click=lambda e: e.page.open(self.dlg_stop_modal)
        )

        self.range_card = ft.ResponsiveRow([
            self.min_torque,
            self.max_torque,
            self.min_speed,
            self.max_speed,
            self.min_thrust,
            self.max_thrust,
            self.min_revolution,
            self.max_revolution
        ])

        self.sps1_instant_data_card = ft.ResponsiveRow(
            alignment=ft.alignment.center,
            controls=[
                self.get_uniform_text(
                    self.page.session.get('lang.common.torque')),
                self.get_uniform_text("0"),
                self.get_uniform_text(
                    self.page.session.get('lang.common.speed')),
                self.get_uniform_text("0"),
                self.get_uniform_text(
                    self.page.session.get('lang.common.thrust')),
                self.get_uniform_text("0"),
                self.get_uniform_text(
                    self.page.session.get('lang.common.revolution')),
                self.get_uniform_text("0")
            ]
        )
        if self.system_settings.amount_of_propeller == 1:
            self.instant_data_cards = CustomCard(
                f'sps1 {self.page.session.get('lang.setting.test_mode.instant_mock_data')}',
                self.sps1_instant_data_card
            )
        else:
            self.sps2_instant_data_card = ft.ResponsiveRow(
                alignment=ft.alignment.center,
                controls=[
                    self.get_uniform_text(
                        self.page.session.get('lang.common.torque')),
                    self.get_uniform_text("0"),
                    self.get_uniform_text(
                        self.page.session.get('lang.common.speed')),
                    self.get_uniform_text("0"),
                    self.get_uniform_text(
                        self.page.session.get('lang.common.thrust')),
                    self.get_uniform_text("0"),
                    self.get_uniform_text(
                        self.page.session.get('lang.common.revolution')),
                    self.get_uniform_text("0")
                ]
            )

            self.instant_data_cards = ft.ResponsiveRow(
                controls=[
                    CustomCard(
                        f'sps1 {self.page.session.get('lang.setting.test_mode.instant_mock_data')}',
                        self.sps1_instant_data_card
                    ),
                    CustomCard(
                        f'sps2 {self.page.session.get('lang.setting.test_mode.instant_mock_data')}',
                        self.sps2_instant_data_card
                    )
                ]
            )

        self.content = ft.Column(
            controls=[
                CustomCard(
                    self.page.session.get(
                        'lang.setting.test_mode.customize_data_range'),
                    self.range_card
                ),
                self.instant_data_cards,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.save_button,
                        self.start_button,
                        self.stop_button
                    ]
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

    def save_test_mode_conf(self, e):
        try:
            min_torque = self.convert_torque(self.min_torque.value)
            max_torque = self.convert_torque(self.max_torque.value)
            min_thrust = self.convert_thrust(self.min_thrust.value)
            max_thrust = self.convert_thrust(self.max_thrust.value)
            min_rev = int(self.min_revolution.value)
            max_rev = int(self.max_revolution.value)
            min_speed = int(self.min_speed.value)
            max_speed = int(self.max_speed.value)

            TestModeConf.update(
                min_torque=min_torque,
                max_torque=max_torque,
                min_speed=min_speed,
                max_speed=max_speed,
                min_thrust=min_thrust,
                max_thrust=max_thrust,
                min_revolution=min_rev,
                max_revolution=max_rev
            ).where(TestModeConf.id == self.test_mode_conf.id).execute()
            Toast.show_success(self.page)
        except Exception as e:
            print(e)
            Toast.show_error(self.page, str(e))

    def start_test_mode(self, e):
        if self.running:
            return

        try:
            min_torque = self.convert_torque(self.min_torque.value)
            max_torque = self.convert_torque(self.max_torque.value)
            self.test_mode_task.set_torque_range(min_torque, max_torque)

            min_speed = int(self.min_speed.value)
            max_speed = int(self.max_speed.value)
            self.test_mode_task.set_speed_range(min_speed, max_speed)

            min_thrust = self.convert_thrust(self.min_thrust.value)
            max_thrust = self.convert_thrust(self.max_thrust.value)
            self.test_mode_task.set_thrust_range(min_thrust, max_thrust)

            min_rev = int(self.min_revolution.value)
            max_rev = int(self.max_revolution.value)
            self.test_mode_task.set_revolution_range(min_rev, max_rev)

            self.page.run_task(self.test_mode_task.start)
            self.page.close(self.dlg_start_modal)
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

        self.test_mode_task.stop()
        self.page.close(self.dlg_stop_modal)
        self.running = False
        self.start_button.visible = True
        self.start_button.update()
        self.stop_button.visible = False
        self.stop_button.update()
        self.save_button.visible = True
        self.save_button.update()

        self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_AUDIO, False)
        self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_FULLSCREEN, False)
        self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_EEXI_OCCURED_FOR_BADGE, False)
        self.page.pubsub.send_all_on_topic(PubSubTopic.BREACH_POWER_OVERLOAD_OCCURED, False)
        Toast.show_success(self.page)

    def did_mount(self):
        self.task = self.page.run_task(self.refresh_current_range_card)

    async def refresh_current_range_card(self):
        system_unit = self.preference.system_unit
        while True:
            if self.running:
                sps1_torque = gdata.sps1_torque
                sps1_speed = gdata.sps1_speed
                sps1_thrust = gdata.sps1_thrust
                sps1_revolution = gdata.sps1_rounds
                sps1_torque_value, sps1_torque_unit = UnitParser.parse_torque(sps1_torque, system_unit)
                self.sps1_instant_data_card.controls[1].value = f'{sps1_torque_value} {sps1_torque_unit}'
                self.sps1_instant_data_card.controls[3].value = f'{sps1_speed} rpm'
                sps1_thrust_value, sps1_thrust_unit = UnitParser.parse_thrust(sps1_thrust, system_unit)
                self.sps1_instant_data_card.controls[5].value = f'{sps1_thrust_value} {sps1_thrust_unit}'
                self.sps1_instant_data_card.controls[7].value = sps1_revolution
                self.sps1_instant_data_card.update()

                if self.system_settings.amount_of_propeller == 2:
                    sps2_torque = gdata.sps2_torque
                    sps2_speed = gdata.sps2_speed
                    sps2_thrust = gdata.sps2_thrust
                    sps2_revolution = gdata.sps2_rounds
                    sps2_torque_value, sps2_torque_unit = UnitParser.parse_torque(
                        sps2_torque, system_unit)
                    self.sps2_instant_data_card.controls[
                        1].value = f'{sps2_torque_value} {sps2_torque_unit}'
                    self.sps2_instant_data_card.controls[3].value = f'{sps2_speed} rpm'
                    sps2_thrust_value, sps2_thrust_unit = UnitParser.parse_thrust(
                        sps2_thrust, system_unit)
                    self.sps2_instant_data_card.controls[
                        5].value = f'{sps2_thrust_value} {sps2_thrust_unit}'
                    self.sps2_instant_data_card.controls[7].value = sps2_revolution
                    self.sps2_instant_data_card.update()

            await asyncio.sleep(1)

    def will_unmount(self):
        if self.task:
            self.task.cancel()
