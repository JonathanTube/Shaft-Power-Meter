import asyncio
import ipaddress
import logging
import flet as ft
from common.operation_type import OperationType
from db.models.io_conf import IOConf
from db.models.operation_log import OperationLog
from db.models.user import User
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from utils.plc_util import plc_util
from common.global_data import gdata


class IOSettingPLC(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.plc_enabled = ft.Checkbox(
            label=self.page.session.get("lang.setting.plc_enabled"), 
            value=self.conf.plc_enabled, col={'sm':12},
            on_change=lambda e : self.__plc_enabled_change(e)
        )

        self.connect_to_plc = ft.FilledButton(
            text = self.page.session.get("lang.setting.connect"),
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            visible=self.conf.plc_enabled and not gdata.connected_to_plc,
            on_click=lambda e: self.page.open(PermissionCheck(self.__on_connect, 2))
        )

        self.disconnect_from_plc = ft.FilledButton(
            text = self.page.session.get("lang.setting.disconnect"),
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE,
            visible=self.conf.plc_enabled and gdata.connected_to_plc,
            on_click=lambda e: self.page.open(PermissionCheck(self.__on_disconnect, 2))
        )

        self.fetch_data_from_plc = ft.FilledButton(
            text = self.page.session.get("lang.setting.fetch_data"),
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE,
            visible=self.conf.plc_enabled and gdata.connected_to_plc,
            on_click=lambda e: self.__on_fetch_data_from_plc()
        )

        self.plc_ip = ft.TextField(
            label=self.page.session.get("lang.setting.ip"), value=self.conf.plc_ip,
            can_request_focus=False,
            read_only=True, on_click=lambda e: keyboard.open(e.control, 'ip'), 
            visible=self.conf.plc_enabled
        )

        self.plc_port = ft.TextField(
            label=self.page.session.get("lang.setting.port"), value=self.conf.plc_port,
            can_request_focus=False,
            read_only=True, on_click=lambda e: keyboard.open(e.control, 'int'), 
            visible=self.conf.plc_enabled
        )

        self.txt_power_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_min"),
            suffix_text='kW',
            col={'sm': 6},
            read_only=True,
            value=0,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int'),
            visible=self.conf.plc_enabled
        )
        self.txt_power_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_max"),
            suffix_text='kW',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_power_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_offset"),
            suffix_text='kW',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )

        self.txt_torque_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_min"),
            suffix_text='kNm',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_torque_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_max"),
            suffix_text='kNm',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_torque_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_offset"),
            suffix_text='kNm',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )

        self.txt_thrust_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_min"),
            suffix_text='kN',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_thrust_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_max"),
            suffix_text='kN',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_thrust_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_offset"),
            suffix_text='kN',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )

        self.txt_speed_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_min"),
            suffix_text='rpm',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_speed_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_max"),
            suffix_text='rpm',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_speed_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_offset"),
            suffix_text='rpm',
            col={'sm': 6},
            read_only=True,
            value=0,
            visible=self.conf.plc_enabled,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )

        self.heading = self.page.session.get("lang.setting.plc_conf")
        
        self.body = ft.ResponsiveRow(controls=[
            self.plc_enabled,
            ft.Row(
                col={'sm':12},
                controls=[
                    self.plc_ip,
                    self.plc_port,
                    self.connect_to_plc,
                    self.disconnect_from_plc,
                    self.fetch_data_from_plc
                ]
            ),
            self.txt_power_range_min,
            self.txt_power_range_max,
            self.txt_power_range_offset,

            self.txt_torque_range_min,
            self.txt_torque_range_max,
            self.txt_torque_range_offset,

            self.txt_thrust_range_min,
            self.txt_thrust_range_max,
            self.txt_thrust_range_offset,

            self.txt_speed_range_min,
            self.txt_speed_range_max,
            self.txt_speed_range_offset,
        ])
        self.col = {'sm': 12}
        super().build()

    def __on_connect(self, user: User):
        if not self.conf.plc_enabled:
            Toast.show_warning(self.page, self.page.session.get('lang.setting.save_conf_before_operations'))
            return
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.CONNECT_TO_PLC,
            operation_content=user.user_name
        )
        self.conf.plc_ip = self.plc_ip.value
        self.conf.plc_port = self.plc_port.value
        self.conf.save()

        self.__start_plc_task()

    def __start_plc_task(self):
        try:
            self.connect_to_plc.text = self.page.session.get("lang.common.connecting")
            self.connect_to_plc.disabled = True
            self.connect_to_plc.update()
            self.page.run_task(plc_util.auto_reconnect, only_once=True)
            self.__handle_plc_connection_status()
        except Exception as e:
            logging.exception(e)

    def __on_disconnect(self, user:User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.DISCONNECT_FROM_PLC,
            operation_content=user.user_name
        )
        self.__stop_plc_task()

    def __stop_plc_task(self):
        try:
            plc_util.close()
            self.__handle_plc_connection_status()
        except Exception as e:
            logging.exception(e)

    def __on_fetch_data_from_plc(self):
        self.page.run_task(self.load_range_data)

    async def load_range_data(self):
        try:
            plc_4_20_ma_data = await plc_util.read_4_20_ma_data()
            self.txt_power_range_min.value = plc_4_20_ma_data["power_range_min"] // 10
            self.txt_power_range_min.update()
            self.txt_power_range_max.value = plc_4_20_ma_data["power_range_max"] // 10
            self.txt_power_range_max.update()
            self.txt_power_range_offset.value = plc_4_20_ma_data["power_range_offset"] // 10
            self.txt_power_range_offset.update()

            self.txt_torque_range_min.value = plc_4_20_ma_data["torque_range_min"] // 10
            self.txt_torque_range_min.update()
            self.txt_torque_range_max.value = plc_4_20_ma_data["torque_range_max"] // 10
            self.txt_torque_range_max.update()
            self.txt_torque_range_offset.value = plc_4_20_ma_data["torque_range_offset"] // 10
            self.txt_torque_range_offset.update()

            self.txt_thrust_range_min.value = plc_4_20_ma_data["thrust_range_min"] // 10
            self.txt_thrust_range_min.update()
            self.txt_thrust_range_max.value = plc_4_20_ma_data["thrust_range_max"] // 10
            self.txt_thrust_range_max.update()
            self.txt_thrust_range_offset.value = plc_4_20_ma_data["thrust_range_offset"] // 10
            self.txt_thrust_range_offset.update()

            self.txt_speed_range_min.value = plc_4_20_ma_data["speed_range_min"] // 10
            self.txt_speed_range_min.update()
            self.txt_speed_range_max.value = plc_4_20_ma_data["speed_range_max"] // 10
            self.txt_speed_range_max.update()
            self.txt_speed_range_offset.value = plc_4_20_ma_data["speed_range_offset"] // 10
            self.txt_speed_range_offset.update()
        except Exception as e:
            logging.exception(e)

    def save_data(self):
        try:
            ipaddress.ip_address(self.plc_ip.value)
        except ValueError:
            raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.plc_ip.value}')

        self.conf.plc_ip = self.plc_ip.value
        self.conf.plc_port = self.plc_port.value
        self.conf.plc_enabled = self.plc_enabled.value
        gdata.plc_enabled = self.plc_enabled.value

        if not self.conf.plc_enabled:
            plc_util.close()
            
        if self.conf.plc_enabled:
            self.page.run_task(self.__write_to_plc)

    def __plc_enabled_change(self, e):
        plc_enabled = e.data
        if plc_enabled == 'true':
            self.connect_to_plc.visible = plc_enabled and not gdata.connected_to_plc
            self.disconnect_from_plc.visible = plc_enabled and gdata.connected_to_plc
            self.fetch_data_from_plc.visible = plc_enabled and gdata.connected_to_plc
        else:
            self.connect_to_plc.visible = False
            self.disconnect_from_plc.visible = False
            self.fetch_data_from_plc.visible = False

        self.connect_to_plc.update()
        self.disconnect_from_plc.update()
        self.fetch_data_from_plc.update()

        self.plc_ip.visible = plc_enabled
        self.plc_ip.update()

        self.plc_port.visible = plc_enabled
        self.plc_port.update()

        self.txt_power_range_min.visible = plc_enabled
        self.txt_power_range_min.update()
        self.txt_power_range_max.visible = plc_enabled
        self.txt_power_range_max.update()
        self.txt_power_range_offset.visible = plc_enabled
        self.txt_power_range_offset.update()

        self.txt_torque_range_min.visible = plc_enabled
        self.txt_torque_range_min.update()
        self.txt_torque_range_max.visible = plc_enabled
        self.txt_torque_range_max.update()
        self.txt_torque_range_offset.visible = plc_enabled
        self.txt_torque_range_offset.update()

        self.txt_thrust_range_min.visible = plc_enabled
        self.txt_thrust_range_min.update()
        self.txt_thrust_range_max.visible = plc_enabled
        self.txt_thrust_range_max.update()
        self.txt_thrust_range_offset.visible = plc_enabled
        self.txt_thrust_range_offset.update()

        self.txt_speed_range_min.visible = plc_enabled
        self.txt_speed_range_min.update()
        self.txt_speed_range_max.visible = plc_enabled
        self.txt_speed_range_max.update()
        self.txt_speed_range_offset.visible = plc_enabled
        self.txt_speed_range_offset.update()

    async def __write_to_plc(self):
        try:
            # 传递给PLC的单位最小是0.1,PLC无法显示0.1，所以乘以10, 所以量程和偏移量也要乘以10
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
            await plc_util.write_4_20_ma_data(data)

        except Exception:
            logging.exception("plc save data error")

    
    def __handle_plc_connection_status(self):
        self.connect_to_plc.text = self.page.session.get("lang.setting.connect")
        self.connect_to_plc.visible = not gdata.connected_to_plc
        self.connect_to_plc.disabled = False
        self.connect_to_plc.update()

        self.disconnect_from_plc.visible = gdata.connected_to_plc
        self.disconnect_from_plc.update()

        self.fetch_data_from_plc.visible = gdata.connected_to_plc
        self.fetch_data_from_plc.update()

    def did_mount(self):
        self.loop_task = self.page.run_task(self.__handle_connection_status)

    def will_unmount(self):
        if self.loop_task:
            self.loop_task.cancel()
    
    async def __handle_connection_status(self):
        while True:
            await asyncio.sleep(1)

            try:
                if not self.plc_enabled.value:
                    continue

                if not self.connect_to_plc.disabled:
                    self.__handle_plc_connection_status()
            except Exception as e:
                logging.exception(e)