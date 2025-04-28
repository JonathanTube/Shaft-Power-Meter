import ipaddress
import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard


class IOSettingSPS1(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.sps1_ip = ft.TextField(
            label=self.page.session.get("lang.setting.ip"),
            value=self.conf.sps1_ip,
            read_only=True,
            col={"sm": 6},
            on_focus=lambda e: keyboard.open(e.control, 'ip')
        )

        self.sps1_port = ft.TextField(
            label=self.page.session.get("lang.setting.port"),
            value=self.conf.sps1_port,
            read_only=True,
            col={"sm": 6},
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.heading = self.page.session.get("lang.setting.sps1_conf")
        self.body = ft.ResponsiveRow(controls=[self.sps1_ip, self.sps1_port])
        self.col = {"sm": 12}
        super().build()

    def save_data(self):
        self.conf.sps1_ip = self.sps1_ip.value
        try:
            ipaddress.ip_address(self.sps1_ip.value)
        except ValueError:
            raise Exception(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps1_ip.value}')

        self.conf.sps1_port = self.sps1_port.value
