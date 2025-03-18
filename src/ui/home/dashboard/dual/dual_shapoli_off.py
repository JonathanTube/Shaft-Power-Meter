import flet as ft

from ui.common.meter_round import MeterRound


class DualShaPoLiOff(ft.Container):
    def __init__(self):
        super().__init__()
        self.big_meter_radius = 75
        self.small_meter_radius = 65
        self.content = self.__create()
        self.expand = False

    def __create_sps1(self):
        self.speed_meter = MeterRound(
            heading="Speed",
            radius=self.small_meter_radius,
            value=80,
            max_value=100,
            limit_value=90,
            unit="rpm",
            shadow=False
        )
        self.power_meter = MeterRound(
            heading="Power",
            radius=self.big_meter_radius,
            value=80,
            max_value=100,
            limit_value=90,
            unit="kW",
            shadow=False
        )
        self.torque_meter = MeterRound(
            heading="Torque",
            radius=self.small_meter_radius,
            value=80,
            max_value=100,
            limit_value=90,
            unit="kNm",
            shadow=False
        )
        row_sps1 = ft.Row(
            # expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                self.speed_meter,
                self.power_meter,
                self.torque_meter
            ])

        return ft.Container(
            expand=False,
            content=row_sps1,
            border_radius=10,
            padding=ft.padding.only(left=10, right=10, top=10, bottom=10),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=4,
                color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE),
                offset=ft.Offset(0, 1),
                blur_style=ft.ShadowBlurStyle.OUTER
            )
        )

    def __create_sps2(self):
        self.speed_meter = MeterRound(
            heading="Speed",
            radius=self.small_meter_radius,
            value=80,
            max_value=100,
            limit_value=90,
            unit="rpm",
            shadow=False
        )
        self.power_meter = MeterRound(
            heading="Power",
            radius=self.big_meter_radius,
            value=80,
            max_value=100,
            limit_value=90,
            unit="kW",
            shadow=False
        )
        self.torque_meter = MeterRound(
            heading="Torque",
            radius=self.small_meter_radius,
            value=80,
            max_value=100,
            limit_value=90,
            unit="kNm",
            shadow=False
        )
        row_sps2 = ft.Row(
            # expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                self.speed_meter,
                self.power_meter,
                self.torque_meter
            ])

        return ft.Container(
            expand=False,
            content=row_sps2,
            border_radius=10,
            padding=ft.padding.only(left=10, right=10, top=10, bottom=10),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=4,
                color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE),
                offset=ft.Offset(0, 1),
                blur_style=ft.ShadowBlurStyle.OUTER
            )
        )

    def __create(self):
        return ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                self.__create_sps1(),
                self.__create_sps2()
            ])
