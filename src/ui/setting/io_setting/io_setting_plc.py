import ipaddress
import logging
import asyncio
import flet as ft
from common.const_alarm_type import AlarmType
from common.operation_type import OperationType
from db.models.io_conf import IOConf
from db.models.operation_log import OperationLog
from db.models.user import User
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from utils.alarm_saver import AlarmSaver
from task.plc_sync_task import plc
from common.global_data import gdata


class IOSettingPLC(ft.Container):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        try:
            if self.page and self.page.session:
                self.plc_enabled = ft.Checkbox(
                    label=self.page.session.get("lang.setting.plc_enabled"),
                    value=self.conf.plc_enabled, col={'sm': 12},
                    on_change=lambda e: self.__plc_enabled_change(e)
                )

                self.connect_btn = ft.FilledButton(
                    text=self.page.session.get("lang.setting.connect"),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    visible=False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(
                        PermissionCheck(self.__on_connect, 2)
                    )
                )

                self.close_btn = ft.FilledButton(
                    text=self.page.session.get("lang.setting.disconnect"),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    visible=False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(
                        PermissionCheck(self.__on_close, 2)
                    )
                )

                self.fetch_btn = ft.FilledButton(
                    text=self.page.session.get("lang.setting.fetch_data"),
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE,
                    visible=False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.run_task(self.on_fetch)
                )

                # ----------------- 输入框 -----------------
                self.plc_ip = ft.TextField(
                    label=self.page.session.get("lang.setting.ip"),
                    value=self.conf.plc_ip,
                    col={'sm': 4},
                    can_request_focus=False,
                    read_only=True, on_click=lambda e: keyboard.open(e.control, 'ip')
                )

                self.plc_port = ft.TextField(
                    label=self.page.session.get("lang.setting.port"),
                    value=self.conf.plc_port,
                    can_request_focus=False,
                    col={'sm': 4},
                    read_only=True, on_click=lambda e: keyboard.open(e.control, 'int')
                )

                # 范围输入框批量创建
                def range_field(label, unit):
                    return ft.TextField(
                        label=label,
                        suffix_text=unit,
                        col={'sm': 4},
                        read_only=True,
                        value=0,
                        can_request_focus=False,
                        on_click=lambda e: keyboard.open(e.control, 'int')
                    )

                self.txt_power_range_min = range_field(self.page.session.get("lang.setting.4_20_ma_power_min"), 'kW')
                self.txt_power_range_max = range_field(self.page.session.get("lang.setting.4_20_ma_power_max"), 'kW')
                self.txt_power_range_offset = range_field(self.page.session.get("lang.setting.4_20_ma_power_offset"), 'kW')

                self.txt_torque_range_min = range_field(self.page.session.get("lang.setting.4_20_ma_torque_min"), 'kNm')
                self.txt_torque_range_max = range_field(self.page.session.get("lang.setting.4_20_ma_torque_max"), 'kNm')
                self.txt_torque_range_offset = range_field(self.page.session.get("lang.setting.4_20_ma_torque_offset"), 'kNm')

                self.txt_thrust_range_min = range_field(self.page.session.get("lang.setting.4_20_ma_thrust_min"), 'kN')
                self.txt_thrust_range_max = range_field(self.page.session.get("lang.setting.4_20_ma_thrust_max"), 'kN')
                self.txt_thrust_range_offset = range_field(self.page.session.get("lang.setting.4_20_ma_thrust_offset"), 'kN')

                self.txt_speed_range_min = range_field(self.page.session.get("lang.setting.4_20_ma_speed_min"), 'rpm')
                self.txt_speed_range_max = range_field(self.page.session.get("lang.setting.4_20_ma_speed_max"), 'rpm')
                self.txt_speed_range_offset = range_field(self.page.session.get("lang.setting.4_20_ma_speed_offset"), 'rpm')

                self.range_items = ft.ResponsiveRow(
                    controls=[
                        self.txt_power_range_min, self.txt_power_range_max, self.txt_power_range_offset,
                        self.txt_torque_range_min, self.txt_torque_range_max, self.txt_torque_range_offset,
                        self.txt_thrust_range_min, self.txt_thrust_range_max, self.txt_thrust_range_offset,
                        self.txt_speed_range_min, self.txt_speed_range_max, self.txt_speed_range_offset
                    ]
                )

                self.plc_enabled_items = ft.Container(
                    visible=self.conf.plc_enabled,
                    content=ft.ResponsiveRow(
                        controls=[
                            self.plc_ip,
                            self.plc_port,
                            ft.Row(
                                alignment=ft.alignment.center_left,
                                col={'sm': 4},
                                controls=[self.connect_btn, self.close_btn, self.fetch_btn],
                            ),
                            self.range_items
                        ])
                )

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.plc_conf"),
                    ft.Column(
                        controls=[
                            self.plc_enabled,
                            self.plc_enabled_items,
                        ]
                    ))

                self.content = self.custom_card
        except:
            logging.exception('exception occured at IOSettingPLC.build')

    def before_update(self):
        try:
            if self.page and self.page.session:
                if self.connect_btn:
                    self.connect_btn.text = self.page.session.get("lang.setting.connect")
                    self.connect_btn.visible = not plc.is_online
                    self.connect_btn.disabled = False
                    self.connect_btn.bgcolor = ft.Colors.GREEN

                if self.close_btn:
                    self.close_btn.text = self.page.session.get("lang.setting.disconnect")
                    self.close_btn.visible = plc.is_online
                    self.close_btn.disabled = False
                    self.close_btn.bgcolor = ft.Colors.RED

                if self.fetch_btn:
                    self.fetch_btn.text = self.page.session.get("lang.setting.fetch_data")
                    self.fetch_btn.visible = plc.is_online
                    self.fetch_btn.disabled = False
                    self.fetch_btn.bgcolor = ft.Colors.BLUE
        except:
            logging.exception('exception occured at IOSettingPLC.before_update')

    def __on_connect(self, user: User):
        try:
            self.save_data()
            self.conf.save()
        except Exception as e:
            Toast.show_error(self.page, str(e))
            return

        try:
            self.connect_btn.text = 'loading...'
            self.connect_btn.disabled = True
            self.connect_btn.bgcolor = ft.Colors.GREY
            self.connect_btn.update()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.configDateTime.utc,
                operation_type=OperationType.CONNECT_TO_PLC,
                operation_content=user.user_name
            )
            self.page.run_task(plc.connect)
        except:
            logging.exception("exception occured at io_setting_plc.__start_plc_task")

    def __on_close(self, user: User):
        try:
            self.close_btn.text = 'loading...'
            self.close_btn.disabled = True
            self.close_btn.bgcolor = ft.Colors.GREY
            self.close_btn.update()

            self.fetch_btn.visible = False
            self.fetch_btn.update()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.configDateTime.utc,
                operation_type=OperationType.DISCONNECT_FROM_PLC,
                operation_content=user.user_name
            )
            self.page.run_task(plc.close)
            plc.save_plc_alarm()
        except:
            logging.exception('exception occured at __stop_plc_task')

    async def on_fetch(self):
        if self.page:
            await self.load_range_data()

    async def load_range_data(self):
        try:
            if self.conf.plc_enabled:
                plc_4_20_ma_data = await asyncio.wait_for(plc.read_4_20_ma_data(), timeout=5)
                logging.info(f'load plc_4_20_ma_data = {plc_4_20_ma_data}')

                self.txt_power_range_min.value = plc_4_20_ma_data["power_range_min"] // 10
                self.txt_power_range_max.value = plc_4_20_ma_data["power_range_max"] // 10
                self.txt_power_range_offset.value = plc_4_20_ma_data["power_range_offset"] // 10

                self.txt_torque_range_min.value = plc_4_20_ma_data["torque_range_min"] // 10
                self.txt_torque_range_max.value = plc_4_20_ma_data["torque_range_max"] // 10
                self.txt_torque_range_offset.value = plc_4_20_ma_data["torque_range_offset"] // 10

                self.txt_thrust_range_min.value = plc_4_20_ma_data["thrust_range_min"] // 10
                self.txt_thrust_range_max.value = plc_4_20_ma_data["thrust_range_max"] // 10
                self.txt_thrust_range_offset.value = plc_4_20_ma_data["thrust_range_offset"] // 10

                self.txt_speed_range_min.value = plc_4_20_ma_data["speed_range_min"] // 10
                self.txt_speed_range_max.value = plc_4_20_ma_data["speed_range_max"] // 10
                self.txt_speed_range_offset.value = plc_4_20_ma_data["speed_range_offset"] // 10

                self.range_items.update()
        except asyncio.TimeoutError:
            logging.warning("读取 PLC 4-20mA 数据超时")
        except:
            logging.exception('exception occured at load_range_data')

    def save_data(self):
        try:
            ipaddress.ip_address(self.plc_ip.value)
        except ValueError:
            raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.plc_ip.value}')

        self.conf.plc_ip = self.plc_ip.value
        self.conf.plc_port = self.plc_port.value
        self.conf.plc_enabled = self.plc_enabled.value

        if self.conf.plc_enabled:
            self.page.run_task(self.__write_to_plc)
        else:
            self.page.run_task(plc.close)
            AlarmSaver.recovery(AlarmType.MASTER_PLC)

    def __plc_enabled_change(self, e):
        if self.plc_enabled_items and self.plc_enabled_items.page:
            self.plc_enabled_items.visible = True if e.data == 'true' else False
            self.plc_enabled_items.update()

    async def __write_to_plc(self):
        try:
            data = {
                "power_range_min": int(self.txt_power_range_min.value) * 10,
                "power_range_max": int(self.txt_power_range_max.value) * 10,
                "power_range_offset": int(self.txt_power_range_offset.value) * 10,

                "torque_range_min": int(self.txt_torque_range_min.value) * 10,
                "torque_range_max": int(self.txt_torque_range_max.value) * 10,
                "torque_range_offset": int(self.txt_torque_range_offset.value) * 10,

                "thrust_range_min": int(self.txt_thrust_range_min.value) * 10,
                "thrust_range_max": int(self.txt_thrust_range_max.value) * 10,
                "thrust_range_offset": int(self.txt_thrust_range_offset.value) * 10,

                "speed_range_min": int(self.txt_speed_range_min.value) * 10,
                "speed_range_max": int(self.txt_speed_range_max.value) * 10,
                "speed_range_offset": int(self.txt_speed_range_offset.value) * 10
            }
            await asyncio.wait_for(plc.write_4_20_ma_data(data), timeout=5)
        except asyncio.TimeoutError:
            logging.warning("写入 PLC 4-20mA 数据超时")
        except:
            logging.exception("plc save data error")
