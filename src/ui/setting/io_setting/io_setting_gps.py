import ipaddress
import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard


class IOSettingGPS(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.gps_ip = ft.TextField(
            label=self.page.session.get("lang.setting.ip"),
            value=self.conf.gps_ip,
            read_only=True,
            col={"sm": 6},
            on_focus=lambda e: keyboard.open(e.control, 'ip')
        )

        self.gps_port = ft.TextField(
            label=self.page.session.get("lang.setting.port"),
            value=self.conf.gps_port,
            read_only=True,
            col={"sm": 6},
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.heading = self.page.session.get("lang.setting.gps_conf")
        self.body = ft.ResponsiveRow(controls=[self.gps_ip, self.gps_port])
        self.col = {"sm": 12}
        super().build()

    def save_data(self):
        try:
            ipaddress.ip_address(self.gps_ip.value)
        except ValueError:
            raise Exception(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.gps_ip.value}')

        self.conf.gps_ip = self.gps_ip.value
        self.conf.gps_port = self.gps_port.value
