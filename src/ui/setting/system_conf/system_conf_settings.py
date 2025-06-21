import logging
import flet as ft
from common.const_alarm_type import AlarmType
from db.models.operation_log import OperationLog
from db.models.preference import Preference
from db.models.system_settings import SystemSettings
from ui.common.custom_card import CustomCard
from utils.alarm_saver import AlarmSaver
from utils.plc_util import plc_util
from utils.unit_converter import UnitConverter
from ui.common.keyboard import keyboard
from common.operation_type import OperationType
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict
from websocket.websocket_server import ws_server
from websocket.websocket_client import ws_client
from common.global_data import gdata
from task.sps1_read_task import sps1_read_task
from task.sps2_read_task import sps2_read_task

class SystemConfSettings(CustomCard):
    def __init__(self):
        super().__init__()
        self.system_settings: SystemSettings = SystemSettings.get()
        self.preference: Preference = Preference.get()

    def build(self):
        self.mode_master = ft.Radio(value='master', label=self.page.session.get("lang.setting.master"))
        self.mode_slave = ft.Radio(value='slave', label=self.page.session.get("lang.setting.slave"))
        self.running_mode = ft.RadioGroup(
            content=ft.Row([self.mode_master, self.mode_slave]),
            value='master' if self.system_settings.is_master else 'slave'
        )
        self.running_mode_row = ft.Row(
            col={"md": 6},
            controls=[
                ft.Text(
                    self.page.session.get("lang.setting.running_mode"),
                    text_align=ft.TextAlign.RIGHT
                ),
                self.running_mode
            ]
        )
        





        self.display_thrust = ft.Checkbox(
            col={"md": 6}, label=self.page.session.get("lang.setting.display_thrust"),
            value=self.system_settings.display_thrust
        )




        self.sha_po_li = ft.Checkbox(
            col={"md": 6}, label=self.page.session.get("lang.setting.enable_sha_po_li"),
            value=self.system_settings.sha_po_li,
            on_change=self.__on_sha_po_li_change
        )




        self.display_propeller_curve = ft.Checkbox(
            col={"md": 6}, label=self.page.session.get("lang.setting.display_propeller_curve"),
            value=self.system_settings.display_propeller_curve
        )






        eexi_limited_power_value, eexi_limited_power_unit = self.__get_eexi_limited_power()
        self.eexi_limited_power = ft.TextField(
            col={"md": 6},
            label=self.page.session.get("lang.setting.eexi_limited_power"),
            value=eexi_limited_power_value,
            suffix_text=eexi_limited_power_unit,
            visible=self.system_settings.sha_po_li,
            read_only=True,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'float')
        )





        self.eexi_breach_checking_duration = ft.TextField(
            col={"md": 6},
            label=self.page.session.get("lang.setting.eexi_breach_checking_duration"),
            value=self.system_settings.eexi_breach_checking_duration,
            suffix_text="seconds",
            visible=self.system_settings.sha_po_li,
            read_only=True,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )




        self.chk_hide_admin_account = ft.Checkbox(
            col={"md": 6}, label=self.page.session.get("lang.setting.hide_admin_account"),
            value=self.system_settings.hide_admin_account
        )






        self.single_propeller = ft.Radio(value="1", label=self.page.session.get("lang.setting.single_propeller"))
        self.twins_propeller = ft.Radio(value="2", label=self.page.session.get("lang.setting.twins_propeller"))
        self.amount_of_propeller_radios = ft.RadioGroup(
            content=ft.Row([self.single_propeller, self.twins_propeller]),
            value=self.system_settings.amount_of_propeller
        )
        self.amount_of_propeller_row = ft.Row(
            col={"md": 6},
            controls=[
                ft.Text(
                    self.page.session.get("lang.setting.amount_of_propeller"),
                    text_align=ft.TextAlign.RIGHT
                ),
                self.amount_of_propeller_radios
            ]
        )




        self.heading = self.page.session.get("lang.setting.setting")
        self.col = {'xs': 12}
        self.expand = True
        self.body = ft.ResponsiveRow(
            controls=[
                self.running_mode_row,
                self.amount_of_propeller_row,
                self.display_thrust,
                self.display_propeller_curve,
                self.sha_po_li,
                self.chk_hide_admin_account,
                self.eexi_limited_power,
                self.eexi_breach_checking_duration
            ]
        )
        super().build()

    def __on_sha_po_li_change(self, e):
        if self.system_settings.sha_po_li:
            self.eexi_limited_power.visible = True
            self.eexi_breach_checking_duration.visible = True
        else:
            self.eexi_limited_power.visible = False
            self.eexi_breach_checking_duration.visible = False
        self.eexi_limited_power.update()
        self.eexi_breach_checking_duration.update()

    def __get_eexi_limited_power(self) -> tuple[float, str]:
        _eexi_limited_power = self.system_settings.eexi_limited_power
        if self.preference.system_unit == 0:
            return (_eexi_limited_power / 1000, "kW")
        else:
            return (UnitConverter.w_to_shp(_eexi_limited_power), "sHp")

    def save(self, user_id: int):
        if self.page is None:
            return

        try:
            self.system_settings.is_master = True if self.running_mode.value == 'master' else False
            self.system_settings.amount_of_propeller = self.amount_of_propeller_radios.value
            self.system_settings.display_thrust = self.display_thrust.value
            self.system_settings.sha_po_li = self.sha_po_li.value
            self.system_settings.display_propeller_curve = self.display_propeller_curve.value
            self.system_settings.hide_admin_account = self.chk_hide_admin_account.value

            unit = self.preference.system_unit
            if unit == 0:
                self.system_settings.eexi_limited_power = float(self.eexi_limited_power.value) * 1000
            else:
                self.system_settings.eexi_limited_power = UnitConverter.shp_to_w(float(self.eexi_limited_power.value))

            self.system_settings.eexi_breach_checking_duration = self.eexi_breach_checking_duration.value

            self.system_settings.save()

            gdata.amount_of_propeller = self.system_settings.amount_of_propeller
            
            gdata.shapoli = self.system_settings.sha_po_li

            gdata.eexi_breach_checking_duration = int(self.system_settings.eexi_breach_checking_duration)

            gdata.eexi_limited_power = float(self.system_settings.eexi_limited_power)

            OperationLog.create(
                user_id=user_id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.SYSTEM_CONF_SETTING,
                operation_content=model_to_dict(self.system_settings)
            )

            if self.system_settings.is_master:
                # 关闭websocket客户端连接
                self.page.run_task(ws_client.close)
                AlarmSaver.recovery(alarm_type=AlarmType.SLAVE_DISCONNECTED)
            else:
                self.page.run_task(plc_util.close)
                AlarmSaver.recovery(alarm_type=AlarmType.PLC_DISCONNECTED)

                self.page.run_task(ws_server.stop)
                AlarmSaver.recovery(alarm_type=AlarmType.MASTER_SERVER_STOPPED)

                self.page.run_task(sps1_read_task.async_disconnect)
                AlarmSaver.recovery(alarm_type=AlarmType.SPS1_DISCONNECTED)

                self.page.run_task(sps2_read_task.async_disconnect)
                AlarmSaver.recovery(alarm_type=AlarmType.SPS2_DISCONNECTED)
        except:
            logging.exception('exception occured at SystemConfSettings.save')