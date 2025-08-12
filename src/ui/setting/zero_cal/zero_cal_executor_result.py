import logging
import flet as ft
from common.global_data import gdata


class ZeroCalExecutorResult(ft.Card):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def build(self):
        try:
            self.torque_offset = ft.Text(value="/")
            self.thrust_offset = ft.Text(value="/")

            controls = [
                ft.Text(self.page.session.get("lang.zero_cal.new_torque_offset")),
                self.torque_offset
            ]
            if gdata.configCommon.show_thrust:
                controls.append(ft.Text(self.page.session.get("lang.zero_cal.new_thrust_offset")))
                controls.append(self.thrust_offset)

            self.content = ft.Container(
                padding=ft.padding.symmetric(0, 10),
                content=ft.Row(
                    height=40,
                    expand=True,
                    controls=controls
                )
            )
        except:
            logging.exception('exception occured at ZeroCalExecutor.build')

    def update_torque_result(self, avg_torque):
        if avg_torque is None:
            return

        if self.torque_offset and self.torque_offset.page:
            self.torque_offset.value = round(avg_torque, 4)
            self.torque_offset.page.update()

    def update_thrust_result(self, avg_thrust):
        if avg_thrust is None:
            return

        if self.thrust_offset and self.thrust_offset.page:
            self.thrust_offset.value = round(avg_thrust, 4)
            self.thrust_offset.page.update()

    def reset(self):
        self.update_result(0, 0)
