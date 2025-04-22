import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard


class IOSettingOutput(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.check_torque = ft.Checkbox(
            label=self.page.session.get("lang.common.torque"),
            col={'md': 2},
            value=self.conf.output_torque
        )
        self.check_thrust = ft.Checkbox(
            label=self.page.session.get("lang.common.thrust"),
            col={'md': 2},
            value=self.conf.output_thrust
        )

        self.check_power = ft.Checkbox(
            label=self.page.session.get("lang.common.power"),
            col={'md': 2},
            value=self.conf.output_power
        )

        self.check_speed = ft.Checkbox(
            label=self.page.session.get("lang.common.speed"),
            col={'md': 2},
            value=self.conf.output_speed
        )

        self.check_avg_power = ft.Checkbox(
            label=self.page.session.get("lang.common.average_power"),
            col={'md': 2},
            value=self.conf.output_avg_power
        )

        self.check_sum_power = ft.Checkbox(
            label=self.page.session.get("lang.common.sum_power"),
            col={'md': 2},
            value=self.conf.output_sum_power
        )

        self.heading = self.page.session.get("lang.setting.output_conf")
        self.body = ft.ResponsiveRow(controls=[
            self.check_torque,
            self.check_thrust,
            self.check_power,
            self.check_speed,
            self.check_avg_power,
            self.check_sum_power
        ])
        self.col = {"md": 12}
        super().build()
        
    def save_data(self):
        self.conf.output_torque = self.check_torque.value
        self.conf.output_thrust = self.check_thrust.value
        self.conf.output_power = self.check_power.value
        self.conf.output_speed = self.check_speed.value
        self.conf.output_avg_power = self.check_avg_power.value
        self.conf.output_sum_power = self.check_sum_power.value
