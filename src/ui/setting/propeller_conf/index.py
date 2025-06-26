import flet as ft
import logging
from db.models.propeller_setting import PropellerSetting
from db.models.operation_log import OperationLog
from common.operation_type import OperationType
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict
from db.models.system_settings import SystemSettings
from db.models.user import User
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from websocket.websocket_server import ws_server
from ui.setting.propeller_conf.propeller_conf_load_limit_curve import PropellerConfLimitCurve
from ui.setting.propeller_conf.propeller_conf_mcr import PropellerConfMcr
from ui.setting.propeller_conf.propeller_conf_normal_curve import PropellerConfNormalCurve
from ui.setting.propeller_conf.propeller_conf_light_curve import PropellerConfLightCurve
from ui.setting.propeller_conf.propeller_conf_speed_limit_curve import PropellerConfSpeedLimitCurve
from ui.setting.propeller_conf.propeller_conf_overload_curve import PropellerConfOverloadCurve


class PropellerConf(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.alignment = ft.alignment.center
        self.system_settings: SystemSettings = SystemSettings.get()
        self.ps: PropellerSetting = PropellerSetting.get()
        self.is_saving = False

    def build(self):
        if self.page and self.page.session:
            try:
                if not self.system_settings.is_master:
                    self.content = ft.Text(
                        value=self.page.session.get('lang.propeller_curve.disabled_under_slave_mode'),
                        size=20
                    )
                    return

                if not self.system_settings.display_propeller_curve:
                    self.content = ft.Text(
                        self.page.session.get('lang.propeller_curve.propeller_curve_disabled')
                    )
                    return

                self.mcr_operating_point_card = PropellerConfMcr(self.ps)
                self.normal_propeller_curve_card = PropellerConfNormalCurve(self.ps)
                self.torque_load_limit_curve_card = PropellerConfLimitCurve(self.ps)
                self.light_propeller_curve_card = PropellerConfLightCurve(self.ps)
                self.speed_limit_curve_card = PropellerConfSpeedLimitCurve(self.ps)
                self.overload_curve_card = PropellerConfOverloadCurve(self.ps)

                self.save_button = ft.FilledButton(
                    self.page.session.get("lang.button.save"),
                    width=120,
                    height=40,
                    on_click=lambda e: self.page.open(PermissionCheck(self.__save_data, 2))
                )

                self.reset_button = ft.OutlinedButton(
                    self.page.session.get("lang.button.reset"),
                    width=120,
                    height=40,
                    on_click=lambda e: self.__reset_data(e)
                )

                self.push_button = ft.OutlinedButton(
                    self.page.session.get("lang.button.push_to_slave"),
                    height=40,
                    icon_color=ft.Colors.GREEN,
                    icon=ft.Icons.SYNC_OUTLINED,
                    on_click=self.__on_push
                )

                self.content = ft.Column(
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                    controls=[
                        ft.ResponsiveRow(
                            controls=[
                                self.mcr_operating_point_card,
                                self.normal_propeller_curve_card,
                                self.light_propeller_curve_card,
                                self.speed_limit_curve_card,
                                self.torque_load_limit_curve_card,
                                self.overload_curve_card,
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        self.save_button,
                                        self.reset_button,
                                        self.push_button
                                    ]
                                )
                            ]
                        )
                    ]
                )
            except:
                logging.exception('exception occured at PropellerConf.build')

    def __change_buttons(self):
        if self.save_button and self.save_button.page:
            self.save_button.disabled = self.is_saving
            self.save_button.update()

        if self.reset_button and self.reset_button.page:
            self.reset_button.disabled = self.is_saving
            self.reset_button.update()

    def __save_data(self, user: User):
        if self.is_saving:
            return

        try:
            self.is_saving = True
            self.__change_buttons()

            keyboard.close()
            self.mcr_operating_point_card.save_data()
            self.normal_propeller_curve_card.save_data()
            self.torque_load_limit_curve_card.save_data()
            self.light_propeller_curve_card.save_data()
            self.speed_limit_curve_card.save_data()
            self.overload_curve_card.save_data()
            self.ps.save()
            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.PROPELLER_SETTING,
                operation_content=model_to_dict(self.ps)
            )
            Toast.show_success(self.page)
        except:
            logging.exception("propeller conf save data error")
            Toast.show_error(self.page)
        finally:
            self.is_saving = False
            self.__change_buttons()

    def __reset_data(self, e):
        keyboard.close()
        self.ps = PropellerSetting.get()
        self.content.clean()
        self.build()
        Toast.show_success(e.page)

    def __on_push(self, e):
        try:
            if self.page:
                self.__save_data()
                settings: PropellerSetting = PropellerSetting.get()
                data = model_to_dict(settings)
                del data['created_at']
                del data['update_at']
                self.page.run_task(ws_server.broadcast, {
                    'type': 'propeller_setting',
                    "data": data
                })
                Toast.show_success(self.page)
        except:
            Toast.show_error(self.page)
