import asyncio
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
        self.is_saving = False
        self.task_running = False
        self.loop_task = None

    def build(self):
            try:
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

                    if self.system_settings.enable_gps:
                        self.gps_conf = IOSettingGPS(self.conf)
                        controls.append(self.gps_conf)

                    if self.system_settings.is_master:
                        self.plc_conf = IOSettingPLC(self.conf)
                        controls.append(self.plc_conf)
                        self.sps_conf = IOSettingSPS(self.conf)
                        controls.append(self.sps_conf)
                        if not self.system_settings.is_individual:
                            self.master_server_conf = IOSettingMasterServer()
                            controls.append(self.master_server_conf)
                    else:
                        self.interface_conf = InterfaceConf(self.conf)
                        controls.append(self.interface_conf)

                    controls.append(self.output_conf)

                    controls.append(
                        ft.Row(alignment=ft.MainAxisAlignment.CENTER,controls=[self.save_button, self.reset_button])
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

            if self.system_settings.is_master:
                self.plc_conf.save_data()
                self.sps_conf.save_data()
            else:
                self.interface_conf.save_data()

            if self.system_settings.enable_gps:
                self.gps_conf.save_data()

            self.output_conf.save_data()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.configDateTime.utc,
                operation_type=OperationType.IO_CONF,
                operation_content=model_to_dict(self.conf)
            )
            self.conf.save()
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
                self.update()
            except:
                logging.exception("exception occured at IOSetting.__loop")
                return
            finally:
                await asyncio.sleep(5)

    def did_mount(self):
        self.task_running = True
        self.loop_task = self.page.run_task(self.__loop)

    def will_unmount(self):
        self.task_running = False
        if self.loop_task:
            self.loop_task.cancel()
