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
        self.system_settings:SystemSettings = SystemSettings.get()
        self.ps: PropellerSetting = PropellerSetting.get()

    def build(self):
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
            on_click=lambda e: self.__on_save_button_click(e)
        )

        self.reset_button = ft.OutlinedButton(
            self.page.session.get("lang.button.reset"),
            width=120,
            height=40,
            on_click=lambda e: self.__reset_data(e)
        )

        if self.system_settings.display_propeller_curve:
            self.content = ft.Column(
                scroll=ft.ScrollMode.ADAPTIVE,
                controls=[
                    ft.ResponsiveRow(
                        controls=[
                            self.mcr_operating_point_card,
                            self.normal_propeller_curve_card,
                            self.torque_load_limit_curve_card,
                            self.light_propeller_curve_card,
                            self.speed_limit_curve_card,
                            self.overload_curve_card,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    self.save_button,
                                    self.reset_button
                                ]
                            )
                        ]
                    )
                ]
            )
        else:
            self.content = ft.Text(self.page.session.get('lang.propeller_curve.propeller_curve_disabled'))

    def __on_save_button_click(self, e):
        self.page.open(PermissionCheck(self.__save_data, 2))

    def __save_data(self, user: User):
        try:
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
        except Exception:
            logging.exception("propeller conf save data error")
            Toast.show_error(self.page)
        else:
            Toast.show_success(self.page)

    def __reset_data(self, e):
        keyboard.close()
        self.ps = PropellerSetting.get()
        self.content.clean()
        self.build()
        Toast.show_success(e.page)
