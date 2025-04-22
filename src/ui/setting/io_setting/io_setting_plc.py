import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard


class IOSettingPLC(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.plc_ip = ft.TextField(label=self.page.session.get("lang.setting.ip"), value=self.conf.plc_ip, col={'md': 6}, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'ip'))

        self.plc_port = ft.TextField(label=self.page.session.get("lang.setting.port"), value=self.conf.plc_port, col={'md': 6}, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'int'))

        self.power_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_min"),
            value=self.conf.power_range_min,
            suffix_text='kW',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.power_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_max"),
            value=self.conf.power_range_max,
            suffix_text='kW',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.power_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_offset"),
            value=self.conf.power_range_offset,
            suffix_text='kW',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.torque_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_min"),
            value=self.conf.torque_range_min,
            suffix_text='kNm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.torque_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_max"),
            value=self.conf.torque_range_max,
            suffix_text='kNm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.torque_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_offset"),
            value=self.conf.torque_range_offset,
            suffix_text='kNm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.thrust_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_min"),
            value=self.conf.thrust_range_min,
            suffix_text='kN',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.thrust_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_max"),
            value=self.conf.thrust_range_max,
            suffix_text='kN',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.thrust_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_offset"),
            value=self.conf.thrust_range_offset,
            suffix_text='kN',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.speed_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_min"),
            value=self.conf.speed_range_min,
            suffix_text='rpm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.speed_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_max"),
            value=self.conf.speed_range_max,
            suffix_text='rpm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        self.speed_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_offset"),
            value=self.conf.speed_range_offset,
            suffix_text='rpm',
            col={'md': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.heading = self.page.session.get("lang.setting.plc_conf")
        self.body = ft.ResponsiveRow(controls=[
            self.plc_ip,
            self.plc_port,

            self.power_range_min,
            self.power_range_max,
            self.power_range_offset,

            self.torque_range_min,
            self.torque_range_max,
            self.torque_range_offset,

            self.thrust_range_min,
            self.thrust_range_max,
            self.thrust_range_offset,

            self.speed_range_min,
            self.speed_range_max,
            self.speed_range_offset,
        ])
        self.col = {"md": 12}
        super().build()

    def save_data(self):
        self.conf.plc_ip = self.plc_ip.value
        self.conf.plc_port = self.plc_port.value

        self.conf.power_range_min = self.power_range_min.value
        self.conf.power_range_max = self.power_range_max.value
        self.conf.power_range_offset = self.power_range_offset.value

        self.conf.torque_range_min = self.torque_range_min.value
        self.conf.torque_range_max = self.torque_range_max.value
        self.conf.torque_range_offset = self.torque_range_offset.value

        self.conf.thrust_range_min = self.thrust_range_min.value
        self.conf.thrust_range_max = self.thrust_range_max.value
        self.conf.thrust_range_offset = self.thrust_range_offset.value

        self.conf.speed_range_min = self.speed_range_min.value
        self.conf.speed_range_max = self.speed_range_max.value
        self.conf.speed_range_offset = self.speed_range_offset.value
