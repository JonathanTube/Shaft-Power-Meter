import logging
import flet as ft
from ui.common.meter_half import MeterHalf
from common.global_data import gdata


class EEXILimitedPower(ft.Container):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.expand = True

        self.container_width = width
        self.container_height = height

        self.unlimited_power = gdata.configCommon.unlimited_power
        self.eexi_power = gdata.configCommon.eexi_limited_power
        self.normal_power = self.eexi_power * 0.9

        self.blinks = 0

    def build(self):
        try:
            if self.page is None or self.page.window is None or self.page.session is None:
                return

            if self.page.window.height <= 600:
                meter_radius = self.container_height * 0.55
            else:
                meter_radius = self.container_height * 0.56
            green = self.normal_power
            orange = self.eexi_power - self.normal_power
            red = self.unlimited_power - self.eexi_power
            self.meter_half = MeterHalf(radius=meter_radius, green=green, orange=orange, red=red)
            self.title = ft.Text(f"{self.page.session.get('lang.common.eexi_limited_power')}(%)", size=16, weight=ft.FontWeight.W_600)
            self.unlimited_mode = ft.Text(f"{self.page.session.get('lang.common.power_unlimited_mode')}", weight=ft.FontWeight.W_400)
            self.unlimited_mode_icon = ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.GREEN, size=18)

            self.unlimited_mode_row = ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                visible=False,
                controls=[self.unlimited_mode, self.unlimited_mode_icon]
            )

            top_items = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[self.title, self.unlimited_mode_row])

            self.common_alarm_block = ft.Container(
                border_radius=ft.border_radius.all(5),
                padding=ft.padding.only(left=2, right=2, bottom=4),
                alignment=ft.alignment.center,
                content=ft.Text("Common Alarm", color=ft.Colors.WHITE, size=12),
                bgcolor=ft.Colors.RED,
                visible=False
            )

            self.gps_status_block = ft.Container(
                border_radius=ft.border_radius.all(5),
                padding=ft.padding.only(left=2, right=2, bottom=4),
                alignment=ft.alignment.center,
                content=ft.Text("GPS Disconnected", color=ft.Colors.WHITE, size=12),
                bgcolor=ft.Colors.RED,
                visible=False
            )

            identifications = ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.END,
                visible=not gdata.configCommon.is_master,
                controls=[self.gps_status_block, self.common_alarm_block],
                right=4, top=40)

            main_content = ft.Container(
                border=ft.border.all(
                    width=0.5,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)
                ),
                border_radius=10,
                padding=ft.padding.all(10),
                content=ft.Column(
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[top_items, self.meter_half]
                )
            )
            self.content = ft.Stack(controls=[
                identifications,
                main_content
            ])
        except:
            logging.exception('EEXILimitedPower.build')

    def reload(self):
        try:
            if self.page:
                active_value = gdata.configSPS.power

                if gdata.configCommon.is_twins:
                    active_value += gdata.configSPS2.power

                inactive_value = self.unlimited_power - active_value

                if self.meter_half is not None:
                    self.meter_half.set_outer_value(active_value, inactive_value)
                    if self.eexi_power > 0:
                        percentage_of_eexi = round(active_value / self.eexi_power * 100)
                        self.meter_half.set_center_value(percentage_of_eexi)

                self.update_mode()
                self.update_common_alarm()
                self.update_gps_alarm()
                self.blinks += 1
        except:
            logging.exception('EEXILimitedPower.reload')

    def update_common_alarm(self):
        # 主机不更新
        if gdata.configCommon.is_master:
            return

        if not self.common_alarm_block or not self.common_alarm_block.page:
            return

        # 无公共报警发生，并且无未确认公共报警，不显示
        if gdata.configAlarm.alarm_common_count == 0 and gdata.configAlarm.alarm_common_not_ack == 0:
            self.common_alarm_block.visible = False
            self.common_alarm_block.update()
            return

        # 有未确认的报警，闪烁
        if gdata.configAlarm.alarm_common_not_ack > 0:
            # 闪烁
            self.common_alarm_block.visible = self.blinks % 2 == 0
            self.common_alarm_block.update()
            return

        # 有报警常亮
        if gdata.configAlarm.alarm_common_count > 0:
            self.common_alarm_block.visible = True
            self.common_alarm_block.update()

    def update_gps_alarm(self):
        # 主机不更新
        if gdata.configCommon.is_master:
            return

        if not self.gps_status_block or not self.gps_status_block.page:
            return

        # 无GPS报警，无待确认GSP报警，不显示
        if gdata.configAlarm.gps_total_count == 0 and gdata.configAlarm.gps_not_ack == 0:
            self.gps_status_block.visible = False
            self.gps_status_block.update()
            return

        # 未确认GPS报警数量大于0闪烁
        if gdata.configAlarm.gps_not_ack > 0:
            self.gps_status_block.visible = self.blinks % 2 == 0
            self.gps_status_block.update()
            return

        # 有报警常亮
        if gdata.configAlarm.gps_not_ack == 0:
            self.gps_status_block.visible = True
            self.gps_status_block.update()

    def update_mode(self):
        try:
            if self.page:
                instant_power = gdata.configSPS.power
                if gdata.configCommon.is_twins:
                    instant_power += gdata.configSPS2.power

                self.unlimited_mode_row.visible = instant_power > self.normal_power

                if instant_power <= self.eexi_power:
                    self.unlimited_mode_icon.color = ft.Colors.ORANGE
                    self.unlimited_mode.color = ft.Colors.ORANGE
                else:
                    self.unlimited_mode_icon.color = ft.Colors.RED
                    self.unlimited_mode.color = ft.Colors.RED

                if self.unlimited_mode_row and self.unlimited_mode_row.page:
                    self.unlimited_mode_row.update()
        except:
            logging.exception('exception occured at EEXILimitedPower.update_mode')
