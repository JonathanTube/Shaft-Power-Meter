import flet as ft
from db.models.report_info import ReportInfo
from db.models.ship_info import ShipInfo
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings


class ReportInfoDialog(ft.AlertDialog):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.content_width = 750

        self.expand = True
        self.modal = False
        self.scrollable = True
        self.title = ft.Row(
            controls=[
                ft.Text(""),
                ft.Text("Compliance Reporting", expand=True,
                        text_align=ft.TextAlign.CENTER),
                ft.IconButton(
                    icon=ft.icons.CLOSE_OUTLINED,
                    # icon_color=ft.colors.INVERSE_SURFACE,
                    on_click=lambda e: e.page.close(self)
                )
            ]
        )
        self.adaptive_width = True
        self.adaptive_height = True
        self.content_padding = 20
        self.shape = ft.RoundedRectangleBorder(radius=10)
        self.__load_data()

    def __load_data(self):
        self.ship_info = ShipInfo.get()
        self.propeller_setting = PropellerSetting.get()
        self.system_settings = SystemSettings.get()
        self.report_info = ReportInfo.get()
        self.event_log = self.report_info.event_log

    def __create_label(self, text):
        return ft.Text(text, col=4, text_align=ft.TextAlign.LEFT, weight=ft.FontWeight.W_500)

    def __create_value(self, text):
        return ft.Text(text, col=2, text_align=ft.TextAlign.LEFT)

    def __create_container(self, content):
        return ft.Container(
            expand=True,
            content=content,
            bgcolor=ft.colors.ON_INVERSE_SURFACE,
            padding=ft.padding.only(top=20, bottom=20, left=20, right=20),
            border_radius=10
        )

    def __create_basic_info(self):
        basic_info = ft.ResponsiveRow(
            expand=True,
            width=self.content_width,
            controls=[
                self.__create_label("Ship Type:"),
                self.__create_value(self.ship_info.ship_type),

                self.__create_label("Ship Size(DWT):"),
                self.__create_value(self.ship_info.ship_size),

                self.__create_label("IMO Number:"),
                self.__create_value(self.ship_info.imo_number),

                self.__create_label("Ship Name:"),
                self.__create_value(self.ship_info.ship_name),

                self.__create_label("Un-limited Power:"),
                self.__create_value(
                    self.propeller_setting.shaft_power_of_mcr_operating_point),

                self.__create_label("Limited Power:"),
                self.__create_value(self.system_settings.eexi_limited_power)
            ]
        )
        self.basic_info_container = self.__create_container(basic_info)

    def __create_event_start_log(self):
        self.event_start_log = ft.ResponsiveRow(
            expand=True,
            width=self.content_width,
            controls=[
                self.__create_label("Date/Time of Power Reserve Breach:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label("Ship position of power reserve breach:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label("Beaufort number:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label("Wave height:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label("Ice condition:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label("Reason for using the power reserve:"),
                self.__create_value("XXXXXXXXX")
            ]
        )

    def __create_event_end_log(self):
        self.event_end_log = ft.ResponsiveRow(
            expand=True,
            width=self.content_width,
            controls=[
                self.__create_label(
                    "Date/Time when returning to limited power:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label(
                    "Ship position when returning to limited power:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label("Beaufort number:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label("Wave height:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label("Ice condition:"),
                self.__create_value("XXXXXXXXX"),

                self.__create_label("Reason for using the power reserve:"),
                self.__create_value("XXXXXXXXX")
            ]
        )

    def __create_event_log(self):
        title = ft.Text("ShaPoLi Event Log",
                        expand=True,
                        text_align=ft.TextAlign.CENTER,
                        size=16,
                        weight=ft.FontWeight.W_500)
        self.__create_event_start_log()
        self.__create_event_end_log()
        event_log = ft.Column(
            expand=True,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                title,
                self.event_start_log,
                self.event_end_log
            ]
        )

        self.event_log_container = self.__create_container(event_log)

    def __create_data_log(self):
        title = ft.Text("ShaPoLi Data Log",
                        expand=True,
                        text_align=ft.TextAlign.CENTER,
                        size=16,
                        weight=ft.FontWeight.W_500)
        table = ft.DataTable(
            width=self.content_width,
            columns=[
                ft.DataColumn(ft.Text("No.")),
                ft.DataColumn(ft.Text("Date/Time")),
                ft.DataColumn(ft.Text("Speed(rpm)")),
                ft.DataColumn(ft.Text("Torque(kNm)")),
                ft.DataColumn(ft.Text("Power(kW)")),
                ft.DataColumn(ft.Text("Total Power(kW)"))
            ],
            rows=[]
        )
        data_log = ft.Column(
            expand=True,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[title, table]
        )
        self.data_log_container = self.__create_container(data_log)

    def build(self):
        self.__create_basic_info()
        self.__create_event_log()
        self.__create_data_log()

        self.content = ft.Column(
            expand=True,
            controls=[
                self.basic_info_container,
                self.event_log_container,
                self.data_log_container
            ]
        )
