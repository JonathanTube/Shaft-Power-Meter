import logging
from fpdf import FPDF
from db.models.event_log import EventLog
from db.models.report_info import ReportInfo
from db.models.ship_info import ShipInfo
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from db.models.preference import Preference
from db.models.report_detail import ReportDetail
from utils.unit_parser import UnitParser
from db.models.date_time_conf import DateTimeConf


class ReportInfoExporter(FPDF):
    def __init__(self):
        super().__init__()

        datetime_conf: DateTimeConf = DateTimeConf.get()
        self.date_format = datetime_conf.date_format
        self.date_time_format = f"{self.date_format} %H:%M:%S"

        self.per_cell_width = 47.5
        self.add_page()

    def __load_data(self, id: int):
        try:
            self.ship_info: ShipInfo = ShipInfo.get()
            self.propeller_setting: PropellerSetting = PropellerSetting.get()
            self.preference: Preference = Preference.get()
            self.system_settings: SystemSettings = SystemSettings.get()

            self.is_dual = self.system_settings.amount_of_propeller == 2
            self.report_info: ReportInfo = ReportInfo.get_by_id(id)
            self.event_log: EventLog = self.report_info.event_log
            self.report_details: list[ReportDetail] = ReportDetail.select().where(
                ReportDetail.report_info == self.report_info.id
            ).order_by(
                ReportDetail.id.asc()
            )
        except:
            logging.exception('exception occured at ReportInfoExporter.__load_data')

    def generate_pdf(self, path, id: int):
        try:
            self.__load_data(id)

            self.__handle_report_title()

            self.__handle_basic_info()

            self.__handle_event_log()

            self.__handle_data_log()

            self.output(path)
        except:
            logging.exception('exception occured at ReportInfoExporter.__load_data')


    # 设置标题
    def __handle_report_title(self):
        # 设置字体和样式
        self.set_font(family="Arial", style='B', size=16)
        self.set_text_color(51, 51, 51)
        # 主标题
        self.cell(0, 20, "Compliance Reporting", ln=1, align='C')
        self.ln(5)  # 下移5mm

    # 第一部分：基本信息

    def __handle_basic_info(self):
        self.__insert_label("Ship Name", w=self.per_cell_width)
        self.__insert_value(self.ship_info.ship_name, w=self.per_cell_width)
        self.__insert_label("IMO Number", w=self.per_cell_width)
        self.__insert_value(self.ship_info.imo_number, w=self.per_cell_width)
        self.ln()

        self.__insert_label("Ship Size(DWT)", w=self.per_cell_width)
        self.__insert_value(self.ship_info.ship_size, w=self.per_cell_width)
        self.__insert_label("Ship Name", w=self.per_cell_width)
        self.__insert_value(self.ship_info.ship_name, w=self.per_cell_width)
        self.ln()

        system_unit = self.preference.system_unit
        self.__insert_label("Un-limited Power", w=self.per_cell_width)
        unlimited_power = self.propeller_setting.shaft_power_of_mcr_operating_point
        unlimited_power, unlimited_unit = UnitParser.parse_power(unlimited_power, system_unit, shrink=False)
        self.__insert_value(f"{unlimited_power} {unlimited_unit}", w=self.per_cell_width)

        self.__insert_label("Limited Power", w=self.per_cell_width)
        limited_power = self.system_settings.eexi_limited_power
        limited_power, limited_unit = UnitParser.parse_power(limited_power, system_unit, shrink=False)
        self.__insert_value(f"{limited_power} {limited_unit}", w=self.per_cell_width)
        self.ln()

        self.__insert_horizontal_line()

    # 第二部分：ShaPoLi事件日志
    def __handle_event_log(self):
        self.__insert_subtitle('ShaPoLi Event Log')

        self.__handle_event_log_start()

        self.__handle_event_log_end()

    # 第三部分：数据日志表格

    def __handle_data_log(self):
        self.__insert_subtitle('ShaPoLi Data Log')
        self.set_font(family="Arial", size=10)
        self.set_text_color(51, 51, 51)
        # 表头
        col_widths = [12, 38, 35, 35, 35]
        if self.is_dual:
            col_widths.append(35)

        system_unit = self.preference.system_unit

        headers = ["No.", "Date/Time", "Speed"]
        if system_unit == 0:
            headers.append("Torque(kNm)")
            headers.append("Power(kw)")
            if self.is_dual:
                headers.append("Total Power(kw)")
        else:
            headers.append("Torque(Tm)")
            headers.append("Power(sHp)")
            if self.is_dual:
                headers.append("Total Power(sHp)")

        self.set_font("Arial", 'B', 10)

        # 绘制表头
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, border=1)
        self.ln()

        self.set_font("Arial", '', 10)
        self.set_text_color(66, 66, 66)

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
                    if report_detail.name == 'sps':
                        _speed_value = f"{report_detail.speed}"
                        _sps_torque, _ = UnitParser.parse_torque(report_detail.torque, system_unit, shrink=False)
                        _torque_value = f"{_sps_torque}"
                        _sps_power, _ = UnitParser.parse_power(report_detail.power, system_unit, shrink=False)
                        _power_value = f"{_sps_power}"
                        _total_power_value = _sps_power
                    else:
                        _speed_value = f"{_speed_value} ; {report_detail.speed}"
                        _sps2_torque, _ = UnitParser.parse_torque(report_detail.torque, system_unit, shrink=False)
                        _torque_value = f"{_torque_value} ; {_sps2_torque}"
                        _sps2_power, _ = UnitParser.parse_power(report_detail.power, system_unit, shrink=False)
                        _power_value = f"{_power_value} ; {_sps2_power}"
                        _total_power_value = round(_total_power_value + _sps2_power, 1)

                rows.append([
                    str(index + 1),
                    _utc_date_time,
                    _speed_value,
                    _torque_value,
                    _power_value,
                    str(_total_power_value)
                ])
        else:
            for index, report_detail in enumerate(self.report_details):
                if report_detail.utc_date_time:
                    utc_date_time = report_detail.utc_date_time.strftime(self.date_time_format)
                else:
                    utc_date_time = "N/A"

                torque, _ = UnitParser.parse_torque(report_detail.torque, system_unit, shrink=False)
                power, _ = UnitParser.parse_power(report_detail.power, system_unit, shrink=False)

                rows.append([
                    str(index + 1),
                    utc_date_time,
                    f"{report_detail.speed}",
                    f"{torque}",
                    f"{power}"
                ])

        for row in rows:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, item, border=1)
            self.ln()

    def __handle_event_log_start(self):
        label_width = self.per_cell_width * 2
        value_width = self.per_cell_width * 2
        self.__insert_label("Override activation/Reactivation", w=label_width)
        self.__insert_value("activation" if self.event_log.started_at != "N/A" else "N/A", w=value_width)
        self.ln()

        self.__insert_label("Date/Time of Power Reserve Breach", w=label_width)
        if self.event_log.started_at:
            self.__insert_value(self.event_log.started_at.strftime(self.date_time_format), w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)

        self.ln()

        self.__insert_label("Ship position of power reserve breach", w=label_width)
        if self.event_log.started_position:
            self.__insert_value(self.event_log.started_position, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_label("Beaufort number", w=label_width)
        if self.event_log.beaufort_number:
            self.__insert_value(self.event_log.beaufort_number, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_label("Wave height", w=label_width)
        if self.event_log.wave_height:
            self.__insert_value(self.event_log.wave_height, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_label("Ice condition", w=label_width)
        if self.event_log.ice_condition:
            self.__insert_value(self.event_log.ice_condition, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_label("Reason for reserve usage", w=label_width)
        if self.event_log.breach_reason:
            self.__insert_value(
                self.event_log.breach_reason.reason, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_horizontal_line()

    def __handle_event_log_end(self):
        label_width = self.per_cell_width * 2
        value_width = self.per_cell_width * 2

        self.__insert_label("Override activation/Reactivation", w=label_width)
        self.__insert_value("reactivation" if self.event_log.ended_at != "N/A" else "N/A", w=value_width)
        self.ln()

        self.__insert_label(
            "Date/Time when returning to limited power", w=label_width)
        if self.event_log.ended_at:
            self.__insert_value(self.event_log.ended_at.strftime(self.date_time_format), w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_label(
            "Ship position when returning to limited power", w=label_width)
        if self.event_log.ended_position:
            self.__insert_value(self.event_log.ended_position, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_label("Beaufort number", w=label_width)
        if self.event_log.beaufort_number:
            self.__insert_value(self.event_log.beaufort_number, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_label("Wave height", w=label_width)
        if self.event_log.wave_height:
            self.__insert_value(self.event_log.wave_height, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_label("Ice condition", w=label_width)
        if self.event_log.ice_condition:
            self.__insert_value(self.event_log.ice_condition, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_label("Reason for reserve usage", w=label_width)
        if self.event_log.breach_reason:
            self.__insert_value(
                self.event_log.breach_reason.reason, w=value_width)
        else:
            self.__insert_value("N/A", w=value_width)
        self.ln()

        self.__insert_horizontal_line()

        # 插入水平分隔线

    def __insert_horizontal_line(self):
        # self.ln(5)
        # self.set_draw_color(221, 221, 221)
        # self.line(10, self.get_y(), self.w - 10, self.get_y())
        # self.ln(5)
        pass

    def __insert_subtitle(self, title: str):
        self.ln(8)
        self.set_font(family="Arial", style='B', size=12)
        self.set_text_color(51, 51, 51)
        self.cell(0, 10, title, ln=1, align='C')
        self.ln(5)

    def __insert_label(self, text: str, w: int, align: str = 'R'):
        self.set_draw_color(244, 244, 244)
        self.set_text_color(51, 51, 51)
        self.set_font(family="Arial", size=10)
        self.cell(w, 10, f'{text}:', align=align, border=1)

    def __insert_value(self, text: str, w: int, align: str = 'R'):
        self.set_draw_color(244, 244, 244)
        self.set_text_color(66, 66, 66)
        self.set_font(family="Arial", size=10)
        self.cell(w, 10, text, align=align, border=1)


# file_path = 'C:\\Users\\Administrator\\Desktop\\test.pdf'

# if os.path.exists(file_path):
#     os.remove(file_path)

# ReportInfoExporter().generate_pdf(file_path)
