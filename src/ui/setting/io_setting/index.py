import logging
import flet as ft
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from db.models.user import User
from ui.common.toast import Toast
from ui.common.permission_check import PermissionCheck
from ui.setting.io_setting.io_setting_interface import InterfaceConf
from ui.setting.io_setting.io_setting_master_server import IOSettingMasterServer
from ui.setting.io_setting.io_setting_plc import IOSettingPLC
from ui.setting.io_setting.io_setting_gps import IOSettingGPS
from ui.setting.io_setting.io_setting_sps import IOSettingSPS
from ui.setting.io_setting.io_setting_output import IOSettingOutput
from db.models.operation_log import OperationLog
from common.operation_type import OperationType
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict
from ui.common.keyboard import keyboard


class IOSetting(ft.Container):
    def __init__(self):
        super().__init__()
        self.system_settings: SystemSettings = SystemSettings.get()
        self.conf: IOConf = IOConf.get()

    def build(self):
        try:
            self.gps_conf = IOSettingGPS(self.conf)
            self.output_conf = IOSettingOutput(self.conf)

            self.save_button = ft.FilledButton(self.page.session.get("lang.button.save"), width=120, height=40, on_click=lambda e: self.__on_save_button_click(e))
            self.reset_button = ft.OutlinedButton(self.page.session.get("lang.button.reset"), width=120, height=40, on_click=self.__reset_data)

            controls = [
                self.gps_conf,
                self.output_conf,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[self.save_button, self.reset_button]
                )
            ]

            if self.system_settings.is_master:
                self.plc_conf = IOSettingPLC(self.conf)
                controls.insert(1, self.plc_conf)
                self.sps_conf = IOSettingSPS(self.conf)
                controls.insert(2, self.sps_conf)
                self.master_server_conf = IOSettingMasterServer()
                controls.insert(3, self.master_server_conf)
            else:
                self.interface_conf = InterfaceConf(self.conf)
                controls.insert(1, self.interface_conf)

            self.content = ft.Column(
                scroll=ft.ScrollMode.ADAPTIVE,
                expand=True,
                controls=[ft.ResponsiveRow(controls=controls)]
            )
        except:
            logging.exception('exception occured at IOSetting.build')

    def __on_save_button_click(self, e):
        keyboard.close()
        self.page.open(PermissionCheck(self.__save_data, 0))

    def __save_data(self, user: User):
        try:
            keyboard.close()

            if self.system_settings.is_master:
                self.plc_conf.save_data()
                self.sps_conf.save_data()
            else:
                self.interface_conf.save_data()

            self.gps_conf.save_data()
            self.output_conf.save_data()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.IO_CONF,
                operation_content=model_to_dict(self.conf)
            )
            self.conf.save()
            Toast.show_success(self.page)
        except Exception as e:
            Toast.show_error(self.page, str(e))

    def __reset_data(self, e):
        keyboard.close()
        self.conf = IOConf.get()
        self.content.clean()
        self.build()
        Toast.show_success(e.page)
