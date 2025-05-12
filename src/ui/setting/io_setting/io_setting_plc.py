import asyncio
import ipaddress
import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from utils.plc_util import plc_util
from common.global_data import gdata


class IOSettingPLC(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.plc_status = ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            visible=False,
            content=ft.Text(value=self.page.session.get("lang.alarm.plc_disconnected"), weight=ft.FontWeight.BOLD, color=ft.Colors.RED)
        )

        self.write_real_time_data_to_plc = ft.Checkbox(label=self.page.session.get("lang.setting.write_real_time_data_to_plc"), value=self.conf.write_real_time_data_to_plc, col={'md': 12})

        self.plc_ip = ft.TextField(label=self.page.session.get("lang.setting.ip"), value=self.conf.plc_ip, col={'md': 6}, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'ip'))

        self.plc_port = ft.TextField(label=self.page.session.get("lang.setting.port"), value=self.conf.plc_port, col={'md': 6}, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'int'))

        self.txt_power_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_min"),
            suffix_text='kW',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_power_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_max"),
            suffix_text='kW',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_power_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_offset"),
            suffix_text='kW',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.txt_torque_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_min"),
            suffix_text='kNm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_torque_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_max"),
            suffix_text='kNm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_torque_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_offset"),
            suffix_text='kNm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.txt_thrust_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_min"),
            suffix_text='kN',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_thrust_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_max"),
            suffix_text='kN',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_thrust_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_offset"),
            suffix_text='kN',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.txt_speed_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_min"),
            suffix_text='rpm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_speed_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_max"),
            suffix_text='rpm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )
        self.txt_speed_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_offset"),
            suffix_text='rpm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.heading = self.page.session.get("lang.setting.plc_conf")
        self.body = ft.ResponsiveRow(controls=[
            self.plc_status,
            self.write_real_time_data_to_plc,
            self.plc_ip,
            self.plc_port,

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
        self.col = {"md": 12}
        super().build()
        self.page.run_task(self.load_range_data)

    async def load_range_data(self):
        try:
            self.plc_status.visible = not await plc_util.auto_reconnect()
            self.plc_status.update()

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
            pass

    def save_data(self):
        try:
            ipaddress.ip_address(self.plc_ip.value)
        except ValueError:
            raise Exception(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.plc_ip.value}')

        self.conf.plc_ip = self.plc_ip.value
        self.conf.plc_port = self.plc_port.value
        self.conf.write_real_time_data_to_plc = self.write_real_time_data_to_plc.value
        gdata.write_real_time_data_to_plc = self.write_real_time_data_to_plc.value

        self.page.run_task(self.__write_to_plc)

    async def __write_to_plc(self):
        try:
            self.plc_status.visible = not await plc_util.auto_reconnect()
            self.plc_status.update()
        except Exception as e:
            pass

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
