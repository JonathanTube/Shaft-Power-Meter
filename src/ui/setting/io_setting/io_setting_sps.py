import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard

class IOSettingSPS(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.sps_ip = ft.TextField(label=self.page.session.get("lang.setting.ip"), value=self.conf.sps_ip, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'ip'))

        self.sps_port = ft.TextField(label=self.page.session.get("lang.setting.port"), value=self.conf.sps_port, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'int'))

        self.heading = self.page.session.get("lang.setting.sps_conf")
        self.body = ft.ResponsiveRow(controls=[self.sps_ip, self.sps_port])
        self.col = {"sm": 6}
        super().build()

    def save_data(self):
        self.conf.sps_ip = self.sps_ip.value
        self.conf.sps_port = self.sps_port.value
