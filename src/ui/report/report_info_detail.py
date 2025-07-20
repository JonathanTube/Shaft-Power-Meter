import logging
import flet as ft
from db.models.event_log import EventLog
from db.models.report_info import ReportInfo
from db.models.ship_info import ShipInfo
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from db.models.preference import Preference
from db.models.report_detail import ReportDetail
from utils.unit_parser import UnitParser
from db.models.date_time_conf import DateTimeConf


class ReportInfoDialog(ft.AlertDialog):
    def __init__(self, id, report_name):
        super().__init__()

        datetime_conf: DateTimeConf = DateTimeConf.get()
        self.date_format = datetime_conf.date_format
        self.date_time_format = f"{self.date_format} %H:%M:%S"

        system_settings: SystemSettings = SystemSettings.get()
        self.is_dual = system_settings.amount_of_propeller == 2

        self.id = id
        self.report_name = report_name if report_name is not None else ''
        self.content_width = 1000

        self.expand = True
        self.modal = False
        self.scrollable = True
        self.title = ft.Row(
            controls=[
                ft.Text(""),
                ft.Text(report_name, expand=True, text_align=ft.TextAlign.CENTER),
                ft.IconButton(icon=ft.Icons.CLOSE_OUTLINED, on_click=lambda e: e.page.close(self))
            ]
        )
        self.adaptive_width = True
        self.adaptive_height = True
        self.content_padding = 20
        self.shape = ft.RoundedRectangleBorder(radius=10)
        self.__load_data()

    def __load_data(self):
        try:
            self.ship_info: ShipInfo = ShipInfo.get()
            self.propeller_setting: PropellerSetting = PropellerSetting.get()
            self.preference: Preference = Preference.get()
            self.system_settings: SystemSettings = SystemSettings.get()
            self.report_info: ReportInfo = ReportInfo.get_by_id(self.id)

            if self.report_info is not None:
                self.event_log: EventLog = self.report_info.event_log
                # limit the max report details to 200 otherwise the database will be locked
                if self.is_dual:
                    self.report_details: list[ReportDetail] = ReportDetail.select().where(
                        ReportDetail.report_info == self.report_info.id
                    ).order_by(
                        ReportDetail.id.asc()
                    ).limit(250)
                else:
                    self.report_details: list[ReportDetail] = ReportDetail.select().where(
                        ReportDetail.report_info == self.report_info.id,
                        ReportDetail.name == 'sps1'
                    ).order_by(
                        ReportDetail.id.asc()
                    ).limit(250)
        except:
            logging.exception('exception occured at ReportInfoDialog.__load_data')

    def __create_label(self, text, col=4):
        return ft.Text(
            text if text is not None else '',
            col=col, text_align=ft.TextAlign.LEFT, weight=ft.FontWeight.W_500
        )

    def __create_value(self, text, col=2):
        return ft.Text(
            text if text is not None else '',
            col=col, text_align=ft.TextAlign.LEFT
        )

    def __create_container(self, content):
        return ft.Container(
            expand=True,
            content=content,
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            padding=ft.padding.only(top=20, bottom=20, left=20, right=20),
            border_radius=10
        )

    def __create_basic_info(self):
        try:
            unlimited_power = self.propeller_setting.shaft_power_of_mcr_operating_point
            limited_power = self.system_settings.eexi_limited_power
            system_unit = self.preference.system_unit
            unlimited_power_value, unlimited_power_unit = UnitParser.parse_power(unlimited_power, system_unit, shrink=False)
            limited_power_value, limited_power_unit = UnitParser.parse_power(limited_power, system_unit, shrink=False)

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
                    self.__create_value(f"{unlimited_power_value} {unlimited_power_unit}"),

                    self.__create_label("Limited Power:"),
                    self.__create_value(f"{limited_power_value} {limited_power_unit}")
                ]
            )
            self.basic_info_container = self.__create_container(basic_info)
        except:
            logging.exception('exception occured at ReportInfoDialog.__create_basic_info')

    def __create_event_start_log(self):
        try:
            if self.event_log is None:
                return

            if self.event_log.started_at:
                started_at = self.event_log.started_at.strftime(self.date_time_format)
            else:
                started_at = "N/A"

            if self.event_log.started_position:
                started_position = self.event_log.started_position
            else:
                started_position = "N/A"

            if self.event_log.beaufort_number:
                beaufort_number = self.event_log.beaufort_number
            else:
                beaufort_number = "N/A"

            if self.event_log.wave_height:
                wave_height = self.event_log.wave_height
            else:
                wave_height = "N/A"

            if self.event_log.ice_condition:
                ice_condition = self.event_log.ice_condition
            else:
                ice_condition = "N/A"

            if self.event_log.breach_reason:
                reason = self.event_log.breach_reason.reason
            else:
                reason = "N/A"

            self.event_start_log = ft.ResponsiveRow(
                expand=True,
                width=self.content_width,
                controls=[
                    self.__create_label("Override activation/Reactivation:", col=6),
                    self.__create_value("activation" if started_at != "N/A" else "N/A", col=6),

                    self.__create_label("Date/Time of Power Reserve Breach:", col=6),
                    self.__create_value(started_at, col=6),

                    self.__create_label("Ship position of power reserve breach:", col=6),
                    self.__create_value(started_position, col=6),

                    self.__create_label("Beaufort number:", col=6),
                    self.__create_value(beaufort_number, col=6),

                    self.__create_label("Wave height:", col=6),
                    self.__create_value(wave_height, col=6),

                    self.__create_label("Ice condition:", col=6),
                    self.__create_value(ice_condition, col=6),

                    self.__create_label("Reason for using the power reserve:", col=6),
                    self.__create_value(reason, col=6)
                ]
            )
        except:
            logging.exception('exception occured at ReportInfoDialog.__create_event_start_log')

    def __create_event_end_log(self):
        try:
            if self.event_log is None:
                return

            if self.event_log.ended_at:
                ended_at = self.event_log.ended_at.strftime(self.date_time_format)
            else:
                ended_at = "N/A"

            if self.event_log.ended_position:
                ended_position = self.event_log.ended_position
            else:
                ended_position = "N/A"

            if self.event_log.beaufort_number:
                beaufort_number = self.event_log.beaufort_number
            else:
                beaufort_number = "N/A"

            if self.event_log.wave_height:
                wave_height = self.event_log.wave_height
            else:
                wave_height = "N/A"

            if self.event_log.ice_condition:
                ice_condition = self.event_log.ice_condition
            else:
                ice_condition = "N/A"

            if self.event_log.breach_reason:
                reason = self.event_log.breach_reason.reason
            else:
                reason = "N/A"

            self.event_end_log = ft.ResponsiveRow(
                expand=True,
                width=self.content_width,
                controls=[
                    self.__create_label("Override activation/Reactivation:", col=6),
                    self.__create_value("reactivation" if ended_at != "N/A" else "N/A", col=6),

                    self.__create_label("Date/Time when returning to limited power:", col=6),
                    self.__create_value(ended_at, col=6),

                    self.__create_label(
                        "Ship position when returning to limited power:", col=6),
                    self.__create_value(ended_position, col=6),

                    self.__create_label("Beaufort number:", col=6),
                    self.__create_value(beaufort_number, col=6),

                    self.__create_label("Wave height:", col=6),
                    self.__create_value(wave_height, col=6),

                    self.__create_label("Ice condition:", col=6),
                    self.__create_value(ice_condition, col=6),

                    self.__create_label("Reason for using the power reserve:", col=6),
                    self.__create_value(reason, col=6)
                ]
            )
        except:
            logging.exception('exception occured at ReportInfoDialog.__create_event_end_log')

    def __create_event_log(self):
        try:
            controls = []

            title = ft.Text("ShaPoLi Event Log", expand=True, text_align=ft.TextAlign.CENTER, size=16, weight=ft.FontWeight.W_500)
            controls.append(title)

            self.__create_event_start_log()
            if self.event_start_log is not None:
                controls.append(self.event_start_log)

            self.__create_event_end_log()
            if self.event_end_log is not None:
                controls.append(ft.Divider(height=0.5))
                controls.append(self.event_end_log)

            event_log = ft.Column(
                expand=True,
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=controls
            )

            self.event_log_container = self.__create_container(event_log)
        except:
            logging.exception('exception occured at ReportInfoDialog.__create_event_end_log')

    def __create_data_log(self):
        try:
            system_unit = self.preference.system_unit
            title = ft.Text("ShaPoLi Data Log", expand=True, text_align=ft.TextAlign.CENTER, size=16, weight=ft.FontWeight.W_500)

            rows = []

            if self.is_dual:
                # get distinct utc_date_time list from report_details
                utc_date_times = list(set([report_detail.utc_date_time for report_detail in self.report_details]))
                for index, utc_date_time in enumerate(utc_date_times):
                    report_details = [report_detail for report_detail in self.report_details if report_detail.utc_date_time == utc_date_time]

                    _utc_date_time = utc_date_time.strftime(self.date_time_format)
                    _speed_value = ""
                    _torque_value = ""
                    _power_value = ""
                    _total_power_value = 0
                    for report_detail in report_details:
                        if report_detail.name == 'sps1':
                            _speed_value = f"{report_detail.speed}"
                            _sps1_torque, _ = UnitParser.parse_torque(report_detail.torque, system_unit, shrink=False)
                            _torque_value = f"{_sps1_torque}"
                            _sps1_power, _ = UnitParser.parse_power(report_detail.power, system_unit, shrink=False)
                            _power_value = f"{_sps1_power}"
                            _total_power_value = _sps1_power
                        else:
                            _speed_value = f"{_speed_value} ; {report_detail.speed}"
                            _sps2_torque, _ = UnitParser.parse_torque(report_detail.torque, system_unit, shrink=False)
                            _torque_value = f"{_torque_value} ; {_sps2_torque}"
                            _sps2_power, _ = UnitParser.parse_power(report_detail.power, system_unit, shrink=False)
                            _power_value = f"{_power_value} ; {_sps2_power}"
                            _total_power_value = round(_total_power_value + _sps2_power, 1)

                    rows.append(ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(index + 1)),
                            ft.DataCell(ft.Text(_utc_date_time)),
                            ft.DataCell(ft.Text(_speed_value)),
                            ft.DataCell(ft.Text(_torque_value)),
                            ft.DataCell(ft.Text(_power_value)),
                            ft.DataCell(ft.Text(_total_power_value))
                        ]
                    ))

            else:
                for index, report_detail in enumerate(self.report_details):
                    utc_date_time = report_detail.utc_date_time.strftime(self.date_time_format)
                    torque_value, _ = UnitParser.parse_torque(report_detail.torque, system_unit, shrink=False)
                    power_value, _ = UnitParser.parse_power(report_detail.power, system_unit, shrink=False)

                    rows.append(ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(index + 1)),
                            ft.DataCell(ft.Text(utc_date_time)),
                            ft.DataCell(ft.Text(f"{report_detail.speed}")),
                            ft.DataCell(ft.Text(f"{torque_value}")),
                            ft.DataCell(ft.Text(f"{power_value}"))
                        ]
                    ))

            columns = [
                ft.DataColumn(ft.Text("No.")),
                ft.DataColumn(ft.Text("Date/Time")),
                ft.DataColumn(ft.Text(f"Speed(rpm)")),
                ft.DataColumn(ft.Text(f"Torque(kNm)") if system_unit == 0 else ft.Text(f"Torque(Tm)")),
                ft.DataColumn(ft.Text(f"Power(kW)") if system_unit == 0 else ft.Text(f"Power(sHp)")),
            ]
            if self.is_dual:
                columns.append(ft.DataColumn(ft.Text(f"Total Power(kW)") if system_unit == 0 else ft.Text(f"Total Power(sHp)")))

            table = ft.DataTable(
                width=self.content_width,
                columns=columns,
                rows=rows
            )
            data_log = ft.Column(
                expand=True,
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    title,
                    table
                ]
            )
            self.data_log_container = self.__create_container(data_log)
        except:
            logging.exception('exception occured at ReportInfoDialog.__create_data_log')

    def build(self):
        try:
            controls = []

            self.__create_basic_info()
            if self.basic_info_container is not None:
                controls.append(self.basic_info_container)

            self.__create_event_log()
            if self.event_log_container is not None:
                controls.append(self.event_log_container)

            self.__create_data_log()
            if self.data_log_container is not None:
                controls.append(self.data_log_container)

            self.content = ft.Column(
                expand=True,
                controls=controls
            )
        except:
            logging.exception('exception occured at ReportInfoDialog.build')
