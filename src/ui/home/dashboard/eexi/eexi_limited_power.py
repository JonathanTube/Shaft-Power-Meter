import asyncio
import logging
import flet as ft
from peewee import fn
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
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

            self.common_alarm_text = ft.Text("Common Alarm")
            self.common_alarm_dot = ft.Text("🔴")
            self.common_alarm_group = ft.Row(
                controls=[self.common_alarm_text, self.common_alarm_dot],
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )

            self.gps_status_text = ft.Text("GPS Status")
            self.gps_status_dot = ft.Text("🟢")
            self.gps_status_group = ft.Row(
                controls=[self.gps_status_text, self.gps_status_dot],
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )

            identifications = ft.Column(expand=True, alignment=ft.alignment.top_right,
                                        visible=not gdata.configCommon.is_master,
                                        controls=[self.common_alarm_group, self.gps_status_group])

            center_items = ft.Row(expand=True, controls=[self.meter_half, identifications])

            self.content = ft.Container(
                border=ft.border.all(
                    width=0.5,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)
                ),
                border_radius=10,
                padding=ft.padding.all(10),
                content=ft.Column(
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[top_items, center_items]
                )
            )
        except:
            logging.exception('exception occured at EEXILimitedPower.reload')

    def reload(self):
        try:
            if self.page:
                active_value = gdata.configSPS.power

                if gdata.configCommon.amount_of_propeller == 2:
                    active_value += gdata.configSPS2.power

                inactive_value = self.unlimited_power - active_value

                if self.meter_half is not None:
                    self.meter_half.set_outer_value(active_value, inactive_value)
                    if self.eexi_power > 0:
                        percentage_of_eexi = round(active_value / self.eexi_power * 100)
                        self.meter_half.set_center_value(percentage_of_eexi)

                self.update_mode()
                self.page.run_task(self.update_idenfications)
        except:
            logging.exception('exception occured at EEXILimitedPower.reload')

    async def update_idenfications(self):
        try:
            # 在后台线程执行 Peewee 同步查询
            cnt_common_alarm = await asyncio.to_thread(
                lambda: AlarmLog.select(fn.COUNT(AlarmLog.id))
                .where(AlarmLog.alarm_type != AlarmType.MASTER_GPS, AlarmLog.recovery_time == None)
                .scalar()
            )

            cnt_gps_alarm = await asyncio.to_thread(
                lambda: AlarmLog.select(fn.COUNT(AlarmLog.id))
                .where(AlarmLog.alarm_type == AlarmType.MASTER_GPS, AlarmLog.recovery_time == None)
                .scalar()
            )

            # 更新 UI（这里已经回到主线程）
            if self.common_alarm_dot and self.common_alarm_dot.page:
                self.common_alarm_dot.value = '🔴' if cnt_common_alarm > 0 else '🟢'
                self.common_alarm_dot.update()

            if self.gps_status_dot and self.gps_status_dot.page:
                self.gps_status_dot.value = '🔴' if cnt_gps_alarm > 0 else '🟢'
                self.gps_status_dot.update()

        except:
            logging.exception("exception occured at EEXILimitedPower.update_idenfications")

    def update_mode(self):
        try:
            if self.page:
                instant_power = gdata.configSPS.power
                if gdata.configCommon.amount_of_propeller == 2:
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
