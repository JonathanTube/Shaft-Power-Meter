import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard

class IOSettingSPS(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.modbus_ip = ft.TextField(label=self.page.session.get("lang.setting.ip"), value=self.conf.modbus_ip, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'ip'))

        self.modbus_port = ft.TextField(label=self.page.session.get("lang.setting.port"), value=self.conf.modbus_port, read_only=True, on_focus=lambda e: keyboard.open(e.control, 'int'))

        self.heading = self.page.session.get("lang.setting.sps_conf")
        self.body = ft.ResponsiveRow(controls=[self.modbus_ip, self.modbus_port])
        self.col = {"sm": 6}
        super().build()

    def save_data(self):
        self.conf.modbus_ip = self.modbus_ip.value
        self.conf.modbus_port = self.modbus_port.value
