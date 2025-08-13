import asyncio
import logging
import flet as ft
from db.models.io_conf import IOConf
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
        self.is_saving = False
        self.task_running = False
        self.loop_task = None
        self.conf: IOConf = None

    def build(self):
        try:
            self.conf = IOConf.get()
            if self.page and self.page.session:
                self.output_conf = IOSettingOutput(self.conf)

                self.save_button = ft.FilledButton(
                    self.page.session.get("lang.button.save"),
                    width=120, height=40,
                    on_click=lambda e: self.page.open(PermissionCheck(self.__save_data, 0))
                )
                self.reset_button = ft.OutlinedButton(
                    self.page.session.get("lang.button.reset"),
                    width=120, height=40,
                    on_click=self.__reset_data
                )

                controls = []

                if gdata.configCommon.enable_gps:
                    self.gps_conf = IOSettingGPS(self.conf)
                    controls.append(self.gps_conf)

                if gdata.configCommon.is_master:
                    self.plc_conf = IOSettingPLC(self.conf)
                    controls.append(self.plc_conf)
                    self.sps_conf = IOSettingSPS(self.conf)
                    controls.append(self.sps_conf)
                    if not gdata.configCommon.is_individual:
                        self.master_server_conf = IOSettingMasterServer()
                        controls.append(self.master_server_conf)
                else:
                    self.interface_conf = InterfaceConf(self.conf)
                    controls.append(self.interface_conf)

                controls.append(self.output_conf)

                controls.append(
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[self.save_button, self.reset_button])
                )

                self.content = ft.Column(
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                    controls=[ft.ResponsiveRow(controls=controls)]
                )
        except:
            logging.exception('exception occured at IOSetting.build')

    def __save_data(self, user: User):
        if self.is_saving:
            return

        try:
            keyboard.close()

            self.is_saving = True
            self.__change_buttons()

            if gdata.configCommon.is_master:
                self.plc_conf.save_data()
                self.sps_conf.save_data()
            else:
                self.interface_conf.save_data()

            if gdata.configCommon.enable_gps:
                self.gps_conf.save_data()

            self.output_conf.save_data()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.configDateTime.utc,
                operation_type=OperationType.IO_CONF,
                operation_content=model_to_dict(self.conf)
            )
            self.conf.save()
            gdata.set_default_value()
            Toast.show_success(self.page)
        except Exception as e:
            Toast.show_error(self.page, str(e))
        finally:
            self.is_saving = False
            self.__change_buttons()

    def __reset_data(self, e):
        try:
            keyboard.close()
            self.conf = IOConf.get()
            self.content.clean()
            self.build()
            Toast.show_success(e.page)
        except:
            logging.exception('exception occured at IOSetting.__reset_data')

    def __change_buttons(self):
        if self.save_button and self.save_button.page:
            self.save_button.disabled = self.is_saving
            self.save_button.update()

        if self.reset_button and self.reset_button.page:
            self.reset_button.disabled = self.is_saving
            self.reset_button.update()

    async def __loop(self):
        while self.task_running:
            try:
                if gdata.configCommon.enable_gps and self.gps_conf:
                    self.gps_conf.update()

                if self.output_conf:
                    self.output_conf.update()

                if gdata.configCommon.is_master:
                    if not gdata.configCommon.is_individual and self.master_server_conf:
                        self.master_server_conf.update()

                    if self.plc_conf:
                        self.plc_conf.update()

                    if self.sps_conf:
                        self.sps_conf.update()
                else:
                    if self.interface_conf:
                        self.interface_conf.update()
            except:
                logging.exception("exception occured at IOSetting.__loop")
                return
            await asyncio.sleep(8)

    def did_mount(self):
        self.task_running = True
        self.loop_task = self.page.run_task(self.__loop)

    def will_unmount(self):
        self.task_running = False
        if self.loop_task:
            self.loop_task.cancel()
