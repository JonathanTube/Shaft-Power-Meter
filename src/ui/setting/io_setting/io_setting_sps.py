import asyncio
import ipaddress
import logging
import flet as ft
from db.models.user import User
from ui.common.toast import Toast
from db.models.io_conf import IOConf
from db.models.factor_conf import FactorConf
from ui.common.custom_card import CustomCard
from ui.common.permission_check import PermissionCheck
from common.global_data import gdata
from ui.common.keyboard import keyboard
from task.sps_read_task import sps_read_task
from task.sps2_read_task import sps2_read_task


class IOSettingSPS(ft.Container):
    def __init__(self):
        super().__init__()
        self.task = None
        self.task_running = False

    def build(self):
        try:
            if self.page and self.page.session:
                # sps conf. start
                self.sps_ip = ft.TextField(
                    label=f'{self.page.session.get("lang.setting.ip")} SPS',
                    value=gdata.configIO.sps_ip,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'ip')
                )

                self.sps_port = ft.TextField(
                    label=f'{self.page.session.get("lang.setting.port")} SPS',
                    value=gdata.configIO.sps_port,
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
                    visible=sps_read_task.is_online == None or sps_read_task.is_online == False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.connect_sps, 2))
                )

                self.sps_disconnect = ft.FilledButton(
                    text=self.page.session.get("lang.setting.disconnect"),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    col={'sm': 4},
                    visible=sps_read_task.is_online == True,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.close_sps, 2))
                )

                self.sps2_ip = ft.TextField(
                    label=f'{self.page.session.get("lang.setting.ip")} SPS2',
                    value=gdata.configIO.sps2_ip,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'ip')
                )

                self.sps2_port = ft.TextField(
                    label=f'{self.page.session.get("lang.setting.port")} SPS2',
                    value=gdata.configIO.sps2_port,
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
                    visible=sps2_read_task.is_online == None or sps2_read_task == False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.connect_sps2, 2))
                )

                self.sps2_disconnect = ft.FilledButton(
                    text=self.page.session.get("lang.setting.disconnect"),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    col={'sm': 4},
                    visible=sps2_read_task.is_online == True,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.close_sps2, 2))
                )
                # sps conf. end

                # factor conf. start
                self.shaft_outer_diameter = ft.TextField(
                    label=self.page.session.get("lang.setting.bearing_outer_diameter_D"), suffix_text="m",
                    value=gdata.configFactor.bearing_outer_diameter_D,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )

                self.shaft_inner_diameter = ft.TextField(
                    label=self.page.session.get(
                        "lang.setting.bearing_inner_diameter_d"),
                    suffix_text="m",
                    value=gdata.configFactor.bearing_inner_diameter_d,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )

                self.sensitivity_factor_k = ft.TextField(
                    label=self.page.session.get("lang.setting.sensitivity_factor_k"),
                    value=gdata.configFactor.sensitivity_factor_k,
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )

                self.elastic_modulus_E = ft.TextField(
                    label=self.page.session.get("lang.setting.elastic_modulus_E"),
                    value=gdata.configFactor.elastic_modulus_E,
                    suffix_text="Mpa",
                    read_only=True,
                    col={'sm': 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )

                self.poisson_ratio_mu = ft.TextField(
                    label=self.page.session.get("lang.setting.poisson_ratio_mu"),
                    value=gdata.configFactor.poisson_ratio_mu,
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
                    visible=gdata.configCommon.is_twins
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

    def connect_sps(self, user: User):
        try:
            self.save_sps_conf()
            gdata.configIO.set_default_value()
            if self.sps_connect and self.sps_connect.page:
                self.sps_connect.text = 'loading...'
                self.sps_connect.bgcolor = ft.Colors.GREY
                self.sps_connect.disabled = True
                self.sps_connect.update()

            self.page.run_task(sps_read_task.start)
        except Exception as e:
            Toast.show_error(self.page, str(e))

    def close_sps(self, user: User):
        try:
            if self.sps_disconnect and self.sps_disconnect.page:
                self.sps_disconnect.text = 'loading...'
                self.sps_disconnect.bgcolor = ft.Colors.GREY
                self.sps_disconnect.disabled = True
                self.sps_disconnect.update()

            self.page.run_task(sps_read_task.close)
        except:
            logging.exception("exception occured at disconnect_from_sps")

    def connect_sps2(self, user: User):
        try:
            self.save_sps2_conf()
            gdata.configIO.set_default_value()
            if self.sps2_connect and self.sps2_connect.page:
                self.sps2_connect.text = 'loading...'
                self.sps2_connect.bgcolor = ft.Colors.GREY
                self.sps2_connect.disabled = True
                self.sps2_connect.update()

            asyncio.create_task(sps2_read_task.connect())
        except Exception as e:
            Toast.show_error(self.page, str(e))

    def close_sps2(self, user: User):
        try:
            if self.sps2_disconnect and self.sps2_disconnect.page:
                self.sps2_disconnect.text = 'loading...'
                self.sps2_disconnect.bgcolor = ft.Colors.GREY
                self.sps2_disconnect.disabled = True
                self.sps2_disconnect.update()

            self.page.run_task(sps2_read_task.close)
        except:
            logging.exception("exception occured at disconnect_from_sps2")

    def save_data(self):
        self.save_sps_conf()
        self.save_sps2_conf()
        self.save_factor()

    def save_sps_conf(self):
        try:
            ipaddress.ip_address(self.sps_ip.value)
        except ValueError:
            raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps_ip.value}')

        sps_ip = self.sps_ip.value
        sps_port = self.sps_port.value
        IOConf.update(sps_ip=sps_ip, sps_port=sps_port).execute()

    def save_sps2_conf(self):
        if gdata.configCommon.is_twins:
            try:
                ipaddress.ip_address(self.sps2_ip.value)
            except ValueError:
                raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps2_ip.value}')

        sps2_ip = self.sps2_ip.value
        sps2_port = self.sps2_port.value
        IOConf.update(sps2_ip=sps2_ip, sps2_port=sps2_port).execute()

    def save_factor(self):
        bearing_outer_diameter_D = self.shaft_outer_diameter.value
        bearing_inner_diameter_d = self.shaft_inner_diameter.value
        sensitivity_factor_k = self.sensitivity_factor_k.value
        elastic_modulus_E = self.elastic_modulus_E.value
        poisson_ratio_mu = self.poisson_ratio_mu.value

        FactorConf.update(
            bearing_outer_diameter_D=bearing_outer_diameter_D, bearing_inner_diameter_d=bearing_inner_diameter_d,
            sensitivity_factor_k=sensitivity_factor_k, elastic_modulus_E=elastic_modulus_E,
            poisson_ratio_mu=poisson_ratio_mu
        ).execute()
        gdata.configFactor.set_default_value()

    def reset(self):
        try:
            self.update_buttons()
            if self.page and self.page.session:
                # 同步配置数据到控件显示
                self.sps_ip.value = gdata.configIO.sps_ip
                self.sps_port.value = gdata.configIO.sps_port
                if gdata.configCommon.is_twins:
                    self.sps2_ip.value = gdata.configIO.sps2_ip
                    self.sps2_port.value = gdata.configIO.sps2_port

                self.shaft_outer_diameter.value = gdata.configFactor.bearing_outer_diameter_D
                self.shaft_inner_diameter.value = gdata.configFactor.bearing_inner_diameter_d
                self.sensitivity_factor_k.value = gdata.configFactor.sensitivity_factor_k
                self.elastic_modulus_E.value = gdata.configFactor.elastic_modulus_E
                self.poisson_ratio_mu.value = gdata.configFactor.poisson_ratio_mu
        except:
            logging.exception('IOSettingSPS.reset')

    def update_buttons(self):
        try:
            if self.sps_connect and self.sps_connect.page:
                self.sps_connect.text = self.page.session.get("lang.setting.connect")
                self.sps_connect.visible = sps_read_task.is_online == None or sps_read_task.is_online == False
                self.sps_connect.bgcolor = ft.Colors.GREEN
                self.sps_connect.disabled = False

            if self.sps_disconnect and self.sps_disconnect.page:
                self.sps_disconnect.text = self.page.session.get("lang.setting.disconnect")
                self.sps_disconnect.visible = sps_read_task.is_online == True
                self.sps_disconnect.bgcolor = ft.Colors.RED
                self.sps_disconnect.disabled = False

            if gdata.configCommon.is_twins:
                if self.sps2_connect and self.sps2_connect.page:
                    self.sps2_connect.text = self.page.session.get("lang.setting.connect")
                    self.sps2_connect.visible = sps2_read_task.is_online == None or sps2_read_task == False
                    self.sps2_connect.bgcolor = ft.Colors.GREEN
                    self.sps2_connect.disabled = False

                if self.sps2_disconnect and self.sps2_disconnect.page:
                    self.sps2_disconnect.text = self.page.session.get("lang.setting.disconnect")
                    self.sps2_disconnect.visible = sps2_read_task.is_online == True
                    self.sps2_disconnect.bgcolor = ft.Colors.RED
                    self.sps2_disconnect.disabled = False
        except:
            logging.exception('IOSettingSPS.update_buttons')
