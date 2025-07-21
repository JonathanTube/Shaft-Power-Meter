import ipaddress
import logging
import flet as ft
from common.operation_type import OperationType
from db.models.factor_conf import FactorConf
from db.models.io_conf import IOConf
from db.models.operation_log import OperationLog
from db.models.system_settings import SystemSettings
from db.models.user import User
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from common.global_data import gdata
from task.sps_read_task import sps_read_task
from task.sps2_read_task import sps2_read_task
from ui.common.toast import Toast


class IOSettingSPS(ft.Container):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf: IOConf = conf
        self.system_settings: SystemSettings = SystemSettings.get()
        self.is_dual = self.system_settings.amount_of_propeller > 1

        self.factor_conf: FactorConf = FactorConf.get()

        self.task = None
        self.task_running = False

    def build(self):
        try:
            if self.page and self.page.session:
                # sps conf. start
                self.sps_ip = ft.TextField(
                    label=f'{self.page.session.get("lang.setting.ip")} SPS',
                    value=self.conf.sps_ip,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'ip')
                )

                self.sps_port = ft.TextField(
                    label=f'{self.page.session.get("lang.setting.port")} SPS',
                    value=self.conf.sps_port,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'int')
                )

                self.sps_connect = ft.FilledButton(
                    text=self.page.session.get("lang.setting.connect"),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    col={'sm': 4},
                    visible=False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.__connect_sps, 2))
                )

                self.sps_disconnect = ft.FilledButton(
                    text=self.page.session.get("lang.setting.disconnect"),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    col={'sm': 4},
                    visible=False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.__close_sps, 2))
                )

                self.sps2_ip = ft.TextField(
                    label=f'{self.page.session.get("lang.setting.ip")} SPS2',
                    value=self.conf.sps2_ip,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'ip')
                )

                self.sps2_port = ft.TextField(
                    label=f'{self.page.session.get("lang.setting.port")} SPS2',
                    value=self.conf.sps2_port,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'int')
                )

                self.sps2_connect = ft.FilledButton(
                    text=self.page.session.get("lang.setting.connect"),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    col={'sm': 4},
                    visible=False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.__connect_sps2, 2))
                )

                self.sps2_disconnect = ft.FilledButton(
                    text=self.page.session.get("lang.setting.disconnect"),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    col={'sm': 4},
                    visible=False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.__close_sps2, 2))
                )
                # sps conf. end

                # factor conf. start
                self.shaft_outer_diameter = ft.TextField(
                    label=self.page.session.get("lang.setting.bearing_outer_diameter_D"), suffix_text="m",
                    value=self.factor_conf.bearing_outer_diameter_D,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )

                self.shaft_inner_diameter = ft.TextField(
                    label=self.page.session.get(
                        "lang.setting.bearing_inner_diameter_d"),
                    suffix_text="m",
                    value=self.factor_conf.bearing_inner_diameter_d,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )

                self.sensitivity_factor_k = ft.TextField(
                    label=self.page.session.get("lang.setting.sensitivity_factor_k"),
                    value=self.factor_conf.sensitivity_factor_k,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )

                self.elastic_modulus_E = ft.TextField(
                    label=self.page.session.get("lang.setting.elastic_modulus_E"),
                    value=self.factor_conf.elastic_modulus_E,
                    suffix_text="Mpa",
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )

                self.poisson_ratio_mu = ft.TextField(
                    label=self.page.session.get("lang.setting.poisson_ratio_mu"),
                    value=self.factor_conf.poisson_ratio_mu,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )
                # factor conf. end

                self.row_sps = ft.ResponsiveRow(
                    controls=[
                        self.sps_ip,
                        self.sps_port,
                        ft.Row(
                            col={'sm': 4},
                            alignment=ft.alignment.center_left,
                            controls=[
                                self.sps_connect,
                                self.sps_disconnect
                            ]
                        )
                    ]
                )

                self.row_sps2 = ft.ResponsiveRow(
                    controls=[
                        self.sps2_ip,
                        self.sps2_port,
                        ft.Row(
                            col={'sm': 4},
                            alignment=ft.alignment.center_left,
                            controls=[
                                self.sps2_connect,
                                self.sps2_disconnect
                            ])
                    ],
                    visible=self.is_dual
                )

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.sps_conf"),
                    ft.ResponsiveRow(
                        controls=[
                            self.row_sps,
                            self.row_sps2,
                            self.shaft_outer_diameter,
                            self.shaft_inner_diameter,
                            self.sensitivity_factor_k,
                            self.elastic_modulus_E,
                            self.poisson_ratio_mu
                        ]))
                self.content = self.custom_card
        except:
            logging.exception('exception occured at IOSettingSPS.build')

    def __connect_sps(self, user: User):
        try:
            self.save_data()
            self.conf.save()
        except Exception as e:
            Toast.show_error(self.page, str(e))
            return
        
        try:
            self.sps_connect.text = 'loading...'
            self.sps_connect.bgcolor = ft.Colors.GREY
            self.sps_connect.disabled = True
            self.sps_connect.update()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.CONNECT_TO_SPS,
                operation_content=user.user_name
            )

            self.page.run_task(sps_read_task.connect)
        except:
            logging.exception("exception occured at __connect_to_sps")


    def __close_sps(self, user: User):
        try:
            self.sps_disconnect.text = 'loading...'
            self.sps_disconnect.bgcolor = ft.Colors.GREY
            self.sps_disconnect.disabled = True
            self.sps_disconnect.update()
            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.DISCONNECT_FROM_SPS,
                operation_content=user.user_name
            )
            self.page.run_task(sps_read_task.close)
        except:
            logging.exception("exception occured at __disconnect_from_sps")

    def __connect_sps2(self, user: User):
        try:
            self.save_data()
            self.conf.save()
        except Exception as e:
            Toast.show_error(self.page, str(e))
            return

        try:
            self.sps2_connect.text = 'loading...'
            self.sps2_connect.bgcolor = ft.Colors.GREY
            self.sps2_connect.disabled = True
            self.sps2_connect.update()
            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.CONNECT_TO_SPS2,
                operation_content=user.user_name
            )
            self.page.run_task(sps2_read_task.connect)
        except:
            logging.exception("exception occured at __connect_to_sps2")

    def __close_sps2(self, user: User):
        try:
            self.sps2_disconnect.text = 'loading...'
            self.sps2_disconnect.bgcolor = ft.Colors.GREY
            self.sps2_disconnect.disabled = True
            self.sps2_disconnect.update()
            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.DISCONNECT_FROM_SPS2,
                operation_content=user.user_name
            )
            self.page.run_task(sps2_read_task.close)
        except:
            logging.exception("exception occured at __disconnect_from_sps2")

    def save_data(self):
        try:
            ipaddress.ip_address(self.sps_ip.value)
            self.conf.sps_ip = self.sps_ip.value
            self.conf.sps_port = self.sps_port.value
        except ValueError:
            raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps_ip.value}')

        if self.is_dual:
            try:
                ipaddress.ip_address(self.sps2_ip.value)
                self.conf.sps2_ip = self.sps2_ip.value
                self.conf.sps2_port = self.sps2_port.value
            except ValueError:
                raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps2_ip.value}')

        self.save_factor()

    def save_factor(self):
        try:
            self.factor_conf.bearing_outer_diameter_D = self.shaft_outer_diameter.value
            self.factor_conf.bearing_inner_diameter_d = self.shaft_inner_diameter.value
            self.factor_conf.sensitivity_factor_k = self.sensitivity_factor_k.value
            self.factor_conf.elastic_modulus_E = self.elastic_modulus_E.value
            self.factor_conf.poisson_ratio_mu = self.poisson_ratio_mu.value

            self.factor_conf.save()

            gdata.bearing_outer_diameter_D = float(self.shaft_outer_diameter.value)
            gdata.bearing_inner_diameter_d = float(self.shaft_inner_diameter.value)
            gdata.sensitivity_factor_k = float(self.sensitivity_factor_k.value)
            gdata.elastic_modulus_E = float(self.elastic_modulus_E.value)
            gdata.poisson_ratio_mu = float(self.poisson_ratio_mu.value)
            logging.info('factor of gdata was refreshed.')
        except:
            logging.exception('exception occured at IOSettingSPS.save_factor')

    def before_update(self):
        try:
            if self.page and self.page.session:
                if self.sps_connect:
                    self.sps_connect.text = self.page.session.get("lang.setting.connect")
                    self.sps_connect.visible = not sps_read_task.is_connected
                    self.sps_connect.bgcolor = ft.Colors.GREEN
                    self.sps_connect.disabled = False

                if self.sps_disconnect:
                    self.sps_disconnect.text = self.page.session.get("lang.setting.disconnect")
                    self.sps_disconnect.visible = sps_read_task.is_connected
                    self.sps_disconnect.bgcolor = ft.Colors.RED
                    self.sps_disconnect.disabled = False

                if self.is_dual:
                    if self.sps2_connect:
                        self.sps2_connect.text = self.page.session.get("lang.setting.connect")
                        self.sps2_connect.visible = not sps2_read_task.is_connected
                        self.sps2_connect.bgcolor = ft.Colors.GREEN
                        self.sps2_connect.disabled = False

                    if self.sps2_disconnect:
                        self.sps2_disconnect.text = self.page.session.get("lang.setting.disconnect")
                        self.sps2_disconnect.visible = sps2_read_task.is_connected
                        self.sps2_disconnect.bgcolor = ft.Colors.RED
                        self.sps2_disconnect.disabled = False
        except:
            logging.exception('exception occured at IOSettingSPS.before_update')
