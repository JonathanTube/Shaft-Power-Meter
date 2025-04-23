import flet as ft
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard


class IOSettingSPS2(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf
        system_settings: SystemSettings = SystemSettings.get()
        self.amount_of_propeller = system_settings.amount_of_propeller
        self.visible = self.amount_of_propeller == 2

    def build(self):
        self.sps2_ip = ft.TextField(
            label=self.page.session.get("lang.setting.ip"),
            value=self.conf.sps2_ip,
            read_only=True,
            col={"sm": 6},
            on_focus=lambda e: keyboard.open(e.control, 'ip')
        )

        self.sps2_port = ft.TextField(
            label=self.page.session.get("lang.setting.port"),
            value=self.conf.sps2_port,
            read_only=True,
            col={"sm": 6},
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.heading = self.page.session.get("lang.setting.sps2_conf")
        self.body = ft.ResponsiveRow(controls=[self.sps2_ip, self.sps2_port])
        self.col = {"sm": 12}
        super().build()

    def save_data(self):
        self.conf.sps2_ip = self.sps2_ip.value
        self.conf.sps2_port = self.sps2_port.value
