import flet as ft
import logging
from db.models.io_conf import IOConf
from db.models.user import User
from ui.common.toast import Toast
from ui.common.permission_check import PermissionCheck
from ui.setting.io_setting.io_setting_plc import IOSettingPLC
from ui.setting.io_setting.io_setting_gps import IOSettingGPS
from ui.setting.io_setting.io_setting_sps1 import IOSettingSPS1
from ui.setting.io_setting.io_setting_sps2 import IOSettingSPS2
from ui.setting.io_setting.io_setting_output import IOSettingOutput
from ui.setting.io_setting.io_setting_factor import IOSettingFactor
from db.models.opearation_log import OperationLog
from common.operation_type import OperationType
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict
from ui.common.keyboard import keyboard


class IOSetting(ft.Container):
    def __init__(self):
        super().__init__()
        self.conf: IOConf = IOConf.get()

    def build(self):
        self.plc_conf = IOSettingPLC(self.conf)
        self.gps_conf = IOSettingGPS(self.conf)
        self.sps1_conf = IOSettingSPS1(self.conf)
        self.sps2_conf = IOSettingSPS2(self.conf)
        self.output_conf = IOSettingOutput(self.conf)
        self.factor_conf = IOSettingFactor()

        self.save_button = ft.FilledButton(self.page.session.get("lang.button.save"), width=120, height=40, on_click=lambda e: self.__on_save_button_click(e))
        self.reset_button = ft.OutlinedButton(self.page.session.get("lang.button.reset"), width=120, height=40, on_click=self.__reset_data)

        self.content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            controls=[
                ft.ResponsiveRow(
                    controls=[
                        self.plc_conf,
                        self.gps_conf,
                        self.sps1_conf,
                        self.sps2_conf,
                        self.factor_conf,
                        self.output_conf,
                        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[self.save_button, self.reset_button])
                    ]
                )
            ]
        )

    def __on_save_button_click(self, e):
        keyboard.close()
        self.page.open(PermissionCheck(self.__save_data, 0))

    def __save_data(self, user: User):
        try:
            keyboard.close()
            self.plc_conf.save_data()
            self.gps_conf.save_data()
            self.sps1_conf.save_data()
            self.sps2_conf.save_data()
            self.output_conf.save_data()
            self.factor_conf.save_data(user.id)
            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.IO_CONF,
                operation_content=model_to_dict(self.conf)
            )
            Toast.show_success(self.page)
        except Exception as err:
            logging.error(f"io setting save data error: {err}")
            Toast.show_error(self.page, err)

    def __reset_data(self, e):
        keyboard.close()
        self.conf = IOConf.get()
        self.content.clean()
        self.build()
        Toast.show_success(e.page)
