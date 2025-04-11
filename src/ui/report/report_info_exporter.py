from fpdf import FPDF
from db.models.report_info import ReportInfo
from db.models.ship_info import ShipInfo
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from db.models.preference import Preference
from db.models.report_detail import ReportDetail
from utils.unit_parser import UnitParser


class ReportInfoExporter(FPDF):
    def __init__(self):
        super().__init__()
        self.per_cell_width = 47.5
        self.add_page()

    def __load_data(self, id: int):
        self.ship_info = ShipInfo.get()
        self.propeller_setting = PropellerSetting.get()
        self.preference = Preference.get()
        self.system_settings = SystemSettings.get()
        self.report_info = ReportInfo.get_by_id(id)
        self.event_log = self.report_info.event_log
        self.report_details = ReportDetail.select().where(
            ReportDetail.report_info == self.report_info.id).order_by(ReportDetail.id.asc())

    def generate_pdf(self, path, id: int):
        self.__load_data(id)

        self.__handle_report_title()

        self.__handle_basic_info()

        self.__handle_event_log()

        self.__handle_data_log()

        self.output(path)

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

        self.__insert_label("Un-limited Power", w=self.per_cell_width)
        self.__insert_value(
            f"{self.propeller_setting.shaft_power_of_mcr_operating_point} kW", w=self.per_cell_width)
        self.__insert_label("Limited Power", w=self.per_cell_width)
        self.__insert_value(
            f"{self.system_settings.eexi_limited_power} kW", w=self.per_cell_width)
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
        col_widths = [15, 35, 35, 35, 35, 35]
        headers = ["No.", "Date/Time", "Speed", "Torque", "Power", "Total Power"]

        self.set_font("Arial", 'B', 10)

        # 绘制表头
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, border=1)
        self.ln()

        self.set_font("Arial", '', 10)
        self.set_text_color(66, 66, 66)

        rows = []
        for report_detail in self.report_details:
            if report_detail.utc_date_time:
                utc_date_time = report_detail.utc_date_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                utc_date_time = "N/A"
            rows.append([
                str(report_detail.id),
                utc_date_time,
                str(report_detail.speed),
                str(report_detail.torque),
                str(report_detail.power),
                str(report_detail.total_power)
            ])

        for row in rows:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, item, border=1)
            self.ln()

    def __handle_event_log_start(self):
        label_width = self.per_cell_width * 2
        value_width = self.per_cell_width * 2
        
        self.__insert_label("Date/Time of Power Reserve Breach", w=label_width)
        if self.event_log.started_at:
            self.__insert_value(self.event_log.started_at.strftime("%Y-%m-%d %H:%M:%S"), w=value_width)
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
        self.__insert_label(
            "Date/Time when returning to limited power", w=label_width)
        if self.event_log.ended_at:
            self.__insert_value(self.event_log.ended_at.strftime(
                "%Y-%m-%d %H:%M:%S"), w=value_width)
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
