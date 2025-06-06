import ipaddress
from playhouse.shortcuts import model_to_dict
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
from websocket.websocket_server import ws_server
from websocket.websocket_client import ws_client
from common.global_data import gdata
from task.sps1_read_task import sps1_read_task
from task.sps2_read_task import sps2_read_task


class IOSettingSPS(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf: IOConf = conf
        system_settings: SystemSettings = SystemSettings.get()
        self.is_dual = system_settings.amount_of_propeller > 1

        self.factor_conf: FactorConf = FactorConf.get()

    def build(self):
        self.connect_to_sps = ft.Checkbox(
            label=self.page.session.get("lang.setting.connect_to_sps"),
            value=self.conf.connect_to_sps,
            on_change=lambda e: self.__connect_to_sps_changed(e)
        )

        # working as a websocket client start
        self.websocket_server_ip = ft.TextField(
            label=f'HMI {self.page.session.get("lang.setting.ip")}',
            value='0.0.0.0',
            read_only=True
        )

        self.websocket_server_port = ft.TextField(
            label=f'HMI {self.page.session.get("lang.setting.port")}',
            value='8000',
            read_only=True
        )

        self.start_hmi_server = ft.FilledButton(
            text=self.page.session.get("lang.setting.start_hmi_server"),
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            visible=not gdata.hmi_server_started,
            on_click=lambda e: self.page.open(PermissionCheck(self.__start_hmi_server,2))
        )

        self.stop_hmi_server = ft.FilledButton(
            text=self.page.session.get("lang.setting.stop_hmi_server"),
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
            visible=gdata.hmi_server_started,
            on_click=lambda e: self.page.open(PermissionCheck(self.__stop_hmi_server,2))
        )
        # working as a websocket end.

        # sps conf. start
        self.sps1_ip = ft.TextField(
            label=f'{self.page.session.get("lang.setting.ip")} SPS1',
            value=self.conf.sps1_ip,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'ip')
        )

        self.sps1_port = ft.TextField(
            label=f'{self.page.session.get("lang.setting.port")} SPS1',
            value=self.conf.sps1_port,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.sps1_connect = ft.FilledButton(
            text=self.page.session.get("lang.setting.connect"),
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            visible=gdata.sps1_offline,
            on_click=lambda e: self.page.open(PermissionCheck(self.__connect_to_sps1, 2))
        )

        self.sps1_disconnect = ft.FilledButton(
            text=self.page.session.get("lang.setting.disconnect"),
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
            visible=not gdata.sps1_offline,
            on_click=lambda e: self.page.open(PermissionCheck(self.__disconnect_from_sps1, 2))
        )

        self.sps2_ip = ft.TextField(
            label=f'{self.page.session.get("lang.setting.ip")} SPS2',
            value=self.conf.sps2_ip,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'ip')
        )

        self.sps2_port = ft.TextField(
            label=f'{self.page.session.get("lang.setting.port")} SPS2',
            value=self.conf.sps2_port,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.sps2_connect = ft.FilledButton(
            text=self.page.session.get("lang.setting.connect"),
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            visible=gdata.sps2_offline,
            on_click=lambda e: self.page.open(PermissionCheck(self.__connect_to_sps2, 2))
        )

        self.sps2_disconnect = ft.FilledButton(
            text=self.page.session.get("lang.setting.disconnect"),
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
            visible=not gdata.sps2_offline,
            on_click=lambda e: self.page.open(PermissionCheck(self.__disconnect_from_sps2,2))
        )

        self.connect_server = ft.FilledButton(
            text=self.page.session.get("lang.setting.connect_to_hmi_server"),
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            visible=not gdata.connected_to_hmi_server,
            on_click=lambda e: self.page.open(PermissionCheck(self.__connect_to_hmi_server,2))
        )

        self.disconnect_server = ft.FilledButton(
            text=self.page.session.get(
                "lang.setting.disconnect_from_hmi_server"),
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
            visible=gdata.connected_to_hmi_server,
            on_click=lambda e: self.page.open(PermissionCheck(self.__disconnect_from_hmi_server ,2))
        )

        self.hmi_server_ip = ft.TextField(
            label=self.page.session.get("lang.setting.hmi_server_ip"),
            value=self.conf.hmi_server_ip,
            read_only=True
        )

        self.hmi_server_port = ft.TextField(
            label=self.page.session.get("lang.setting.hmi_server_port"),
            value=self.conf.hmi_server_port,
            read_only=True
        )
        # sps conf. end

        # factor conf. start
        self.shaft_outer_diameter = ft.TextField(
            label=self.page.session.get("lang.setting.bearing_outer_diameter_D"), suffix_text="m",
            value=self.factor_conf.bearing_outer_diameter_D,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.shaft_inner_diameter = ft.TextField(
            label=self.page.session.get(
                "lang.setting.bearing_inner_diameter_d"),
            suffix_text="m",
            value=self.factor_conf.bearing_inner_diameter_d,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.sensitivity_factor_k = ft.TextField(
            label=self.page.session.get("lang.setting.sensitivity_factor_k"),
            value=self.factor_conf.sensitivity_factor_k,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.elastic_modulus_E = ft.TextField(
            label=self.page.session.get("lang.setting.elastic_modulus_E"),
            value=self.factor_conf.elastic_modulus_E,
            suffix_text="Mpa",
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.poisson_ratio_mu = ft.TextField(
            label=self.page.session.get("lang.setting.poisson_ratio_mu"),
            value=self.factor_conf.poisson_ratio_mu,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )
        # factor conf. end

        self.heading = self.page.session.get("lang.setting.sps_conf")

        self.row_sps1 = ft.Row(
            controls=[self.sps1_ip, self.sps1_port,
                      self.sps1_connect, self.sps1_disconnect],
            visible=self.conf.connect_to_sps
        )

        self.row_sps2 = ft.Row(
            controls=[self.sps2_ip, self.sps2_port,
                      self.sps2_connect, self.sps2_disconnect],
            visible=self.conf.connect_to_sps and self.is_dual
        )

        self.row_websocket_server = ft.Row(
            controls=[self.websocket_server_ip, self.websocket_server_port,
                      self.start_hmi_server, self.stop_hmi_server],
            visible=self.conf.connect_to_sps
        )

        self.column_factor = ft.Column(
            controls=[
                ft.Row(
                    controls=[self.shaft_outer_diameter, self.shaft_inner_diameter]),
                ft.Row(controls=[self.sensitivity_factor_k,
                       self.elastic_modulus_E]),
                ft.Row(controls=[self.poisson_ratio_mu])
            ],
            visible=self.conf.connect_to_sps
        )

        self.row_websocket_client = ft.Row(
            controls=[self.hmi_server_ip, self.hmi_server_port,
                      self.connect_server, self.disconnect_server],
            visible=not self.conf.connect_to_sps
        )

        self.body = ft.Column(controls=[
            self.connect_to_sps,
            self.row_sps1,
            self.row_sps2,
            self.row_websocket_server,
            self.column_factor,
            self.row_websocket_client
        ])
        self.col = {"sm": 12}
        super().build()

    def __connect_to_sps1(self, user: User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.CONNECT_TO_SPS1,
            operation_content=user.user_name
        )
        self.page.run_task(self.__start_sps1_task)

    async def __start_sps1_task(self):
        connected = await sps1_read_task.start()
        self.sps1_connect.visible = not connected
        self.sps1_connect.update()
        self.sps1_disconnect.visible = connected
        self.sps1_disconnect.update()

    def __disconnect_from_sps1(self, user:User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.DISCONNECT_FROM_SPS1,
            operation_content=user.user_name
        )
        self.page.run_task(self.__stop_sps1_task)

    async def __stop_sps1_task(self):
        disconnected = await sps1_read_task.async_disconnect()
        self.sps1_connect.visible = disconnected
        self.sps1_connect.update()
        self.sps1_disconnect.visible = not disconnected
        self.sps1_disconnect.update()

    def __connect_to_sps2(self, user: User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.CONNECT_TO_SPS2,
            operation_content=user.user_name
        )
        self.page.run_task(self.__start_sps2_task)

    async def __start_sps2_task(self):
        connected = await sps2_read_task.start()
        self.sps2_connect.visible = not connected
        self.sps2_connect.update()
        self.sps2_disconnect.visible = connected
        self.sps2_disconnect.update()

    def __disconnect_from_sps2(self, user:User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.DISCONNECT_FROM_SPS2,
            operation_content=user.user_name
        )
        self.page.run_task(self.__stop_sps2_task)

    async def __stop_sps2_task(self):
        disconnected = await sps2_read_task.async_disconnect()
        self.sps2_connect.visible = disconnected
        self.sps2_connect.update()
        self.sps2_disconnect.visible = not disconnected
        self.sps2_disconnect.update()

    def __start_hmi_server(self, user:User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.START_HMI_SERVER,
            operation_content=user.user_name
        )
        self.page.run_task(self.handle_start_server)

    async def handle_start_server(self):
        started = await ws_server.start()
        self.start_hmi_server.visible = not started
        self.stop_hmi_server.visible = started
        self.start_hmi_server.update()
        self.stop_hmi_server.update()

    def __stop_hmi_server(self, user:User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.STOP_HMI_SERVER,
            operation_content=user.user_name
        )
        self.page.run_task(self.handle_stop_server)

    async def handle_stop_server(self):
        stopped = await ws_server.stop()
        self.start_hmi_server.visible = stopped
        self.stop_hmi_server.visible = not stopped
        self.start_hmi_server.update()
        self.stop_hmi_server.update()

    def __connect_to_hmi_server(self, user: User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.CONNECT_TO_HMI_SERVER,
            operation_content=user.user_name
        )
        self.page.run_task(self.handle_connect_to_hmi_server)

    async def handle_connect_to_hmi_server(self):
        connected = await ws_client.connect()
        self.connect_server.visible = not connected
        self.disconnect_server.visible = connected
        self.connect_server.update()
        self.disconnect_server.update()

    def __disconnect_from_hmi_server(self, user:User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.DISCONNECT_FROM_HMI_SERVER,
            operation_content=user.user_name
        )
        self.page.run_task(self.handle_disconnect_from_hmi_server)

    async def handle_disconnect_from_hmi_server(self):
        closed = await ws_client.close()
        self.connect_server.visible = closed
        self.disconnect_server.visible = not closed
        self.connect_server.update()
        self.disconnect_server.update()

    def __connect_to_sps_changed(self, e):
        is_connect_to_sps = e.control.value
        self.row_sps1.visible = is_connect_to_sps

        self.row_sps2.visible = is_connect_to_sps and self.is_dual

        self.row_websocket_server.visible = is_connect_to_sps

        self.column_factor.visible = is_connect_to_sps

        self.row_websocket_server.visible = is_connect_to_sps

        self.row_websocket_client.visible = not is_connect_to_sps

        self.conf.connect_to_sps = is_connect_to_sps
        self.update()

    def save_data(self):
        try:
            ipaddress.ip_address(self.sps1_ip.value)
            self.conf.sps1_ip = self.sps1_ip.value
            self.conf.sps1_port = self.sps1_port.value
        except ValueError:
            raise Exception(
                f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps1_ip.value}')

        if self.is_dual:
            try:
                ipaddress.ip_address(self.sps2_ip.value)
                self.conf.sps2_ip = self.sps2_ip.value
                self.conf.sps2_port = self.sps2_port.value
            except ValueError:
                raise Exception(
                    f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps2_ip.value}')

        self.save_factor()

        if self.connect_to_sps.value:
            # 关闭websocket客户端连接
            self.page.run_task(ws_client.close)
        else:
            self.page.run_task(ws_server.stop)
            self.page.run_task(sps1_read_task.async_disconnect)
            self.page.run_task(sps2_read_task.async_disconnect)

    def save_factor(self):
        self.factor_conf.bearing_outer_diameter_D = self.shaft_outer_diameter.value
        self.factor_conf.bearing_inner_diameter_d = self.shaft_inner_diameter.value
        self.factor_conf.sensitivity_factor_k = self.sensitivity_factor_k.value
        self.factor_conf.elastic_modulus_E = self.elastic_modulus_E.value
        self.factor_conf.poisson_ratio_mu = self.poisson_ratio_mu.value

        self.factor_conf.save()
