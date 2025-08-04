import logging
import flet as ft


class ZeroCalExecutorResult(ft.Card):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def build(self):
        try:
            self.torque_offset = ft.Text(round(0, 10))
            self.thrust_offset = ft.Text(round(0, 10))

            self.content = ft.Container(
                padding=ft.padding.symmetric(0, 10),
                content=ft.Row(
                    height=40,
                    expand=True,
                    controls=[
                        ft.Text(
                            self.page.session.get(
                                "lang.zero_cal.new_torque_offset")
                        ),
                        
                        self.torque_offset,

                        ft.Text(self.page.session.get(
                            "lang.zero_cal.new_thrust_offset")),

                        self.thrust_offset
                    ]
                )
            )
        except:
            logging.exception('exception occured at ZeroCalExecutor.build')

    def update_result(self, avg_torque, avg_thrust):
        if self.torque_offset and self.torque_offset.page:
            self.torque_offset.value = avg_torque
            self.torque_offset.page.update()

        if self.thrust_offset and self.thrust_offset.page:
            self.thrust_offset.value = avg_thrust
            self.thrust_offset.page.update()
