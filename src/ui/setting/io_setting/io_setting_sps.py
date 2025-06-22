import asyncio
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
from task.sps1_read_task import sps1_read_task
from task.sps2_read_task import sps2_read_task


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
            # sps conf. start
            self.sps1_ip = ft.TextField(
                label=f'{self.page.session.get("lang.setting.ip")} SPS1',
                value=self.conf.sps1_ip,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control, 'ip')
            )

            self.sps1_port = ft.TextField(
                label=f'{self.page.session.get("lang.setting.port")} SPS1',
                value=self.conf.sps1_port,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control, 'int')
            )

            self.sps1_connect = ft.FilledButton(
                text=self.page.session.get("lang.setting.connect"),
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                visible=gdata.sps1_offline,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                on_click=lambda e: self.page.open(PermissionCheck(self.__connect_to_sps1, 2))
            )

            self.sps1_disconnect = ft.FilledButton(
                text=self.page.session.get("lang.setting.disconnect"),
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                visible=not gdata.sps1_offline,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                on_click=lambda e: self.page.open(PermissionCheck(self.__disconnect_from_sps1, 2))
            )

            self.sps2_ip = ft.TextField(
                label=f'{self.page.session.get("lang.setting.ip")} SPS2',
                value=self.conf.sps2_ip,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control, 'ip')
            )

            self.sps2_port = ft.TextField(
                label=f'{self.page.session.get("lang.setting.port")} SPS2',
                value=self.conf.sps2_port,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control, 'int')
            )

            self.sps2_connect = ft.FilledButton(
                text=self.page.session.get("lang.setting.connect"),
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                visible=gdata.sps2_offline,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                on_click=lambda e: self.page.open(PermissionCheck(self.__connect_to_sps2, 2))
            )

            self.sps2_disconnect = ft.FilledButton(
                text=self.page.session.get("lang.setting.disconnect"),
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                visible=not gdata.sps2_offline,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                on_click=lambda e: self.page.open(PermissionCheck(self.__disconnect_from_sps2, 2))
            )
            # sps conf. end

            # factor conf. start
            self.shaft_outer_diameter = ft.TextField(
                label=self.page.session.get("lang.setting.bearing_outer_diameter_D"), suffix_text="m",
                value=self.factor_conf.bearing_outer_diameter_D,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )

            self.shaft_inner_diameter = ft.TextField(
                label=self.page.session.get(
                    "lang.setting.bearing_inner_diameter_d"),
                suffix_text="m",
                value=self.factor_conf.bearing_inner_diameter_d,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )

            self.sensitivity_factor_k = ft.TextField(
                label=self.page.session.get("lang.setting.sensitivity_factor_k"),
                value=self.factor_conf.sensitivity_factor_k,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )

            self.elastic_modulus_E = ft.TextField(
                label=self.page.session.get("lang.setting.elastic_modulus_E"),
                value=self.factor_conf.elastic_modulus_E,
                suffix_text="Mpa",
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )

            self.poisson_ratio_mu = ft.TextField(
                label=self.page.session.get("lang.setting.poisson_ratio_mu"),
                value=self.factor_conf.poisson_ratio_mu,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )
            # factor conf. end

            self.row_sps1 = ft.Row(
                controls=[self.sps1_ip, self.sps1_port, self.sps1_connect, self.sps1_disconnect]
            )

            self.row_sps2 = ft.Row(
                controls=[self.sps2_ip, self.sps2_port, self.sps2_connect, self.sps2_disconnect],
                visible=self.is_dual
            )

            self.column_factor = ft.Column(
                controls=[
                    ft.Row(controls=[self.shaft_outer_diameter, self.shaft_inner_diameter]),
                    ft.Row(controls=[self.sensitivity_factor_k, self.elastic_modulus_E]),
                    ft.Row(controls=[self.poisson_ratio_mu])
                ]
            )

            self.custom_card = CustomCard(
                self.page.session.get("lang.setting.sps_conf"),
                ft.ResponsiveRow(controls=[
                    self.row_sps1,
                    self.row_sps2,
                    self.column_factor
                ]),
                col={"xs": 12})
            self.content = self.custom_card
        except:
            logging.exception('exception occured at IOSettingSPS.build')


    def __connect_to_sps1(self, user: User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.CONNECT_TO_SPS1,
            operation_content=user.user_name
        )
        self.conf.sps1_ip = self.sps1_ip.value
        self.conf.sps1_port = self.sps1_port.value
        self.conf.save()
        self.__start_sps1_task()

    def __start_sps1_task(self):
        try:
            self.sps1_connect.text = self.page.session.get("lang.common.connecting")
            self.sps1_connect.disabled = True
            self.sps1_connect.update()

            self.page.run_task(sps1_read_task.start, only_once=True)
            self.__handle_sps1_connection()
        except Exception as e:
            logging.exception(e)

    def __disconnect_from_sps1(self, user: User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.DISCONNECT_FROM_SPS1,
            operation_content=user.user_name
        )
        self.page.run(sps1_read_task.close)
        self.__handle_sps1_connection()

    def __connect_to_sps2(self, user: User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.CONNECT_TO_SPS2,
            operation_content=user.user_name
        )
        self.conf.sps2_ip = self.sps2_ip.value
        self.conf.sps2_port = self.sps2_port.value
        self.conf.save()
        self.__start_sps2_task()

    def __start_sps2_task(self):
        try:
            self.sps2_connect.text = self.page.session.get("lang.common.connecting")
            self.sps2_connect.disabled = True
            self.sps2_connect.update()

            self.page.run(sps2_read_task.start, only_once=True)
            self.__handle_sps2_connection()
        except Exception as e:
            logging.exception(e)

    def __disconnect_from_sps2(self, user: User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.DISCONNECT_FROM_SPS2,
            operation_content=user.user_name
        )
        self.page.run(sps2_read_task.close)
        self.__handle_sps2_connection()

    def save_data(self):
        try:
            ipaddress.ip_address(self.sps1_ip.value)
            self.conf.sps1_ip = self.sps1_ip.value
            self.conf.sps1_port = self.sps1_port.value
        except ValueError:
            raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps1_ip.value}')

        if self.is_dual:
            try:
                ipaddress.ip_address(self.sps2_ip.value)
                self.conf.sps2_ip = self.sps2_ip.value
                self.conf.sps2_port = self.sps2_port.value
            except ValueError:
                raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps2_ip.value}')

        self.save_factor()

    def save_factor(self):
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

    def __handle_sps1_connection(self):
        self.sps1_connect.text = self.page.session.get("lang.setting.connect")
        self.sps1_connect.visible = gdata.sps1_offline
        self.sps1_connect.disabled = False
        self.sps1_connect.update()

        self.sps1_disconnect.visible = not gdata.sps1_offline
        self.sps1_disconnect.update()

    def __handle_sps2_connection(self):
        self.sps2_connect.text = self.page.session.get("lang.setting.connect")
        self.sps2_connect.visible = gdata.sps2_offline
        self.sps2_connect.disabled = False
        self.sps2_connect.update()

        self.sps2_disconnect.visible = not gdata.sps2_offline
        self.sps2_disconnect.update()

    async def __handle_connection_status(self):
        while self.task_running:
            try:
                if not self.sps1_connect.disabled:
                    self.__handle_sps1_connection()

                if not self.sps2_connect.disabled:
                    self.__handle_sps2_connection()
            except Exception as e:
                logging.exception(e)
            await asyncio.sleep(1)

    def did_mount(self):
        self.task_running = True
        self.task = self.page.run_task(self.__handle_connection_status)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
