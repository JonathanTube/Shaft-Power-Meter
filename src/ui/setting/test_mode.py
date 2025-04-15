import asyncio
import flet as ft

from task.test_mode_task import TestModeTask
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast


class TestMode(ft.Container):
    def __init__(self, test_mode_task: TestModeTask):
        super().__init__()
        self.test_mode_task = test_mode_task
        self.alignment = ft.alignment.top_left
        self.running = False

    def create_abort_dlg(self):
        self.dlg_abort_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please Confirm"),
            content=ft.Text(
                "All of the test data will be deleted. Are you sure you want to abort the test mode?"),
            actions=[
                ft.TextButton(
                    "Confirm", on_click=lambda e: self.abort_test_mode(e)),
                ft.TextButton(
                    "Cancel", on_click=lambda e: e.page.close(self.dlg_abort_modal))
            ]
        )

    def create_start_dlg(self):
        self.dlg_start_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please Confirm"),
            content=ft.Text("Are you sure you want to start the test mode?"),
            actions=[
                ft.TextButton(
                    "Confirm", on_click=lambda e: self.start_test_mode(e)),
                ft.TextButton(
                    "Cancel", on_click=lambda e: e.page.close(self.dlg_start_modal))
            ]
        )

    def build(self):
        self.create_abort_dlg()
        self.create_start_dlg()

        self.min_torque = ft.TextField(
            col={"sm": 12, "md": 6},
            label="Min Torque",
            suffix_text="Nm",
            value=0
        )

        self.max_torque = ft.TextField(
            col={"sm": 12, "md": 6},
            label="Max Torque",
            suffix_text="Nm",
            value=1000
        )

        self.min_speed = ft.TextField(
            col={"sm": 12, "md": 6},
            label="Min Speed",
            suffix_text="RPM",
            value=0
        )

        self.max_speed = ft.TextField(
            col={"sm": 12, "md": 6},
            label="Max Speed",
            suffix_text="RPM",
            value=1000
        )

        self.min_thrust = ft.TextField(
            col={"sm": 12, "md": 6},
            label="Min Thrust",
            suffix_text="N",
            value=0
        )

        self.max_thrust = ft.TextField(
            col={"sm": 12, "md": 6},
            label="Max Thrust",
            suffix_text="N",
            value=1000
        )

        self.min_revolution = ft.TextField(
            col={"sm": 12, "md": 6},
            label="Min Revolution",
            value=0
        )

        self.max_revolution = ft.TextField(
            col={"sm": 12, "md": 6},
            label="Max Revolution",
            value=1000
        )

        self.time_interval = ft.TextField(
            col={"sm": 12, "md": 6},
            label="Generate Data Time Interval",
            suffix_text="seconds",
            value=1
        )

        self.start_button = ft.FilledButton(
            width=150,
            text="Start",
            col={"sm": 12, "md": 6},
            bgcolor=ft.Colors.GREEN,
            on_click=lambda e: e.page.open(self.dlg_start_modal)
        )

        self.abort_button = ft.FilledButton(
            width=150,
            text="Abort",
            col={"sm": 12, "md": 6},
            bgcolor=ft.Colors.RED,
            visible=False,
            on_click=lambda e: e.page.open(self.dlg_abort_modal)
        )

        self.range_card = ft.ResponsiveRow([
            self.min_torque,
            self.max_torque,
            self.min_speed,
            self.max_speed,
            self.min_thrust,
            self.max_thrust,
            self.min_revolution,
            self.max_revolution,
            self.time_interval,
            ft.Row(
                col={"sm": 12, "md": 12},
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.start_button, self.abort_button]
            )
        ])

        self.instant_data_card = ft.ResponsiveRow(
            alignment=ft.alignment.center,
            controls=[
                ft.Text(value=f"Torque:", weight=ft.FontWeight.BOLD, col={"sm": 12, "md": 6}),
                ft.Text(value=f"0", col={"sm": 12, "md": 6}),
                ft.Text(value=f"Speed:", weight=ft.FontWeight.BOLD, col={"sm": 12, "md": 6}),
                ft.Text(value=f"0", col={"sm": 12, "md": 6}),
                ft.Text(value=f"Thrust:", weight=ft.FontWeight.BOLD, col={"sm": 12, "md": 6}),
                ft.Text(value=f"0", col={"sm": 12, "md": 6}),
                ft.Text(value=f"Revolution:", weight=ft.FontWeight.BOLD, col={"sm": 12, "md": 6}),
                ft.Text(value=f"0", col={"sm": 12, "md": 6})
            ]
        )

        self.content = ft.Column(
            controls=[
                CustomCard(
                    'Customize Data Range',
                    self.range_card
                ),
                CustomCard(
                    'Instant Data',
                    self.instant_data_card
                )
            ]
        )

    def start_test_mode(self, e):
        if self.running:
            return

        try:
            self.test_mode_task.set_torque_range(
                int(self.min_torque.value), int(self.max_torque.value))
            self.test_mode_task.set_speed_range(
                int(self.min_speed.value), int(self.max_speed.value))
            self.test_mode_task.set_thrust_range(
                int(self.min_thrust.value), int(self.max_thrust.value))
            self.test_mode_task.set_revolution_range(
                int(self.min_revolution.value), int(self.max_revolution.value))
            self.test_mode_task.set_time_interval(
                int(self.time_interval.value))
            self.page.run_task(self.test_mode_task.start)
            self.page.close(self.dlg_start_modal)
            self.running = True
            self.start_button.visible = False
            self.start_button.update()
            self.abort_button.visible = True
            self.abort_button.update()
            Toast.show_success(self.page)
        except Exception as e:
            Toast.show_error(self.page, str(e))

    def abort_test_mode(self, e):
        if not self.running:
            return

        self.test_mode_task.stop()
        self.page.close(self.dlg_abort_modal)
        self.running = False
        self.start_button.visible = True
        self.start_button.update()
        self.abort_button.visible = False
        self.abort_button.update()
        Toast.show_success(self.page)

    def did_mount(self):
        self.task =self.page.run_task(self.refresh_current_range_card)

    async def refresh_current_range_card(self):
        while True:
            if self.running:
                torque = self.page.session.get('sps1_instant_torque')
                speed = self.page.session.get('sps1_instant_speed')
                thrust = self.page.session.get('sps1_instant_thrust')
                revolution = self.page.session.get('sps1_instant_revolution')
                self.instant_data_card.controls[1].value = torque
                self.instant_data_card.controls[3].value = speed
                self.instant_data_card.controls[5].value = thrust
                self.instant_data_card.controls[7].value = revolution
                self.instant_data_card.update()
            await asyncio.sleep(1)

    def will_unmount(self):
        if self.task:
            self.task.cancel()
