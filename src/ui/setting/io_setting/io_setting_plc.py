import ipaddress
import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from utils.plc_util import PLCUtil


class IOSettingPLC(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.plc_ip = ft.TextField(label=self.page.session.get("lang.setting.ip"), value=self.conf.plc_ip, col={'md': 6}, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'ip'))

        self.plc_port = ft.TextField(label=self.page.session.get("lang.setting.port"), value=self.conf.plc_port, col={'md': 6}, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'int'))

        plc_4_20_ma_data = PLCUtil.read_4_20_ma_data()

        self.txt_power_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_min"),
            value=plc_4_20_ma_data["power_range_min"],
            suffix_text='kW',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.txt_power_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_max"),
            value=plc_4_20_ma_data["power_range_max"],
            suffix_text='kW',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.txt_power_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_offset"),
            value=plc_4_20_ma_data["power_range_offset"],
            suffix_text='kW',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.txt_torque_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_min"),
            value=plc_4_20_ma_data["torque_range_min"],
            suffix_text='kNm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.txt_torque_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_max"),
            value=plc_4_20_ma_data["torque_range_max"],
            suffix_text='kNm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.txt_torque_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_offset"),
            value=plc_4_20_ma_data["torque_range_offset"],
            suffix_text='kNm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.txt_thrust_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_min"),
            value=plc_4_20_ma_data["thrust_range_min"],
            suffix_text='kN',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.txt_thrust_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_max"),
            value=plc_4_20_ma_data["thrust_range_max"],
            suffix_text='kN',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.txt_thrust_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_offset"),
            value=plc_4_20_ma_data["thrust_range_offset"],
            suffix_text='kN',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.txt_speed_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_min"),
            value=plc_4_20_ma_data["speed_range_min"],
            suffix_text='rpm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.txt_speed_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_max"),
            value=plc_4_20_ma_data["speed_range_max"],
            suffix_text='rpm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.txt_speed_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_offset"),
            value=plc_4_20_ma_data["speed_range_offset"],
            suffix_text='rpm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.heading = self.page.session.get("lang.setting.plc_conf")
        self.body = ft.ResponsiveRow(controls=[
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

    def save_data(self):
        try:
            ipaddress.ip_address(self.plc_ip.value)
        except ValueError:
            raise Exception(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.plc_ip.value}')

        self.conf.plc_ip = self.plc_ip.value
        self.conf.plc_port = self.plc_port.value
