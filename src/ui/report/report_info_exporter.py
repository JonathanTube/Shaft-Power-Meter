import os
from fpdf import FPDF


class ReportInfoExporter(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()

    def generate_pdf(self, path):
        self.__handle_report_title()

        self.__handle_basic_info()

        self.__handle_event_log()

        self.__handle_data_log()

        self.output(path)

    # 插入水平分隔线
    def __insert_horizontal_line(self):
        self.ln(5)
        self.set_draw_color(221, 221, 221)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(5)

    def __insert_subtitle(self, title: str):
        self.set_font(family="Arial", style='B', size=12)
        self.cell(0, 10, title, ln=1, align='C')
        self.ln(5)

    def __insert_label(self, text: str, w: int = 35):
        self.set_fill_color(221, 221, 221)
        self.cell(w, 10, f'{text}:', align='L', fill=False)

    def __insert_value(self, text: str, w: int = 60):
        self.set_fill_color(221, 221, 101)
        self.cell(w, 10, text, align='R', fill=False)

    # 设置标题
    def __handle_report_title(self):
        # 设置字体和样式
        self.set_font(family="Arial", style='B', size=16)
        # 主标题
        self.cell(0, 20, "Compliance Reporting", ln=1, align='C')
        self.ln(5)  # 下移5mm

    # 第一部分：基本信息
    def __handle_basic_info(self):
        self.set_font(family="Arial", size=12)

        self.__insert_label("Ship Name")
        self.__insert_value("Chemical Tanker")
        self.__insert_label("IMO Number")
        self.__insert_value("IMO9856724")
        self.ln()

        self.__insert_label("Ship Size(DWT)")
        self.__insert_value("50,000 MT")
        self.__insert_label("Ship Name")
        self.__insert_value("Blue Ocean")
        self.ln()

        self.__insert_label("Un-limited Power")
        self.__insert_value("15,000 kW")
        self.__insert_label("Limited Power")
        self.__insert_value("12,000 kW")
        self.ln()

        self.__insert_horizontal_line()

    def __handle_event_log_start(self):
        self.__insert_label("Date/Time of Power Reserve Breach", w=90)
        self.__insert_value("2025-03-20 14:30 UTC")
        self.ln()

        self.__insert_label("Ship position of power reserve breach", w=90)
        self.__insert_value("35°12'N 139°46'E")
        self.ln()

        self.__insert_label("Beaufort number", w=90)
        self.__insert_value("6")
        self.ln()

        self.__insert_label("Wave height", w=90)
        self.__insert_value("4.2 m")
        self.ln()

        self.__insert_label("Ice condition", w=90)
        self.__insert_value("None")
        self.ln()

        self.__insert_label("Reason for reserve usage", w=90)
        self.__insert_value("Storm avoidance")
        self.ln()

        self.__insert_horizontal_line()

    def __handle_event_log_end(self):
        self.__insert_label("Date/Time when returning to limited power", w=90)
        self.__insert_value("2025-03-20 16:45 UTC")
        self.ln()

        self.__insert_label(
            "Ship position when returning to limited power", w=90)
        self.__insert_value("36°05'N 140°12'E")
        self.ln()

        self.__insert_label("Beaufort number", w=90)
        self.__insert_value("4")
        self.ln()

        self.__insert_label("Wave height", w=90)
        self.__insert_value("2.1 m")
        self.ln()

        self.__insert_label("Ice condition", w=90)
        self.__insert_value("None")
        self.ln()

        self.__insert_label("Reason for reserve usage", w=90)
        self.__insert_value("Storm avoidance")
        self.ln()

        self.__insert_horizontal_line()

    # 第二部分：ShaPoLi事件日志
    def __handle_event_log(self):
        self.__insert_subtitle('ShaPoLi Event Log')
        self.set_font(family="Arial", size=12)

        self.__handle_event_log_start()

        self.__handle_event_log_end()

    # 第三部分：数据日志表格

    def __handle_data_log(self):
        self.__insert_subtitle('ShaPoLi Data Log')
        self.set_font(family="Arial", size=12)
        # 表头
        col_widths = [15, 35, 35, 35, 35, 35]
        headers = ["No.", "Date/Time",
                   "Speed(rpm)", "Torque(kNm)", "Power(kW)", "Total Power(kW)"]

        self.set_font("Arial", 'B', 10)

        # 绘制表头
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, border=1)
        self.ln()

        # 表格数据
        data = [
            ("1", "2025-03-20 14:30", "85", "1200", "4500", "15000"),
            ("2", "2025-03-20 15:00", "82", "1150", "4300", "14800"),
            ("3", "2025-03-20 15:30", "80", "1100", "4100", "14600")
        ]

        self.set_font("Arial", '', 10)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, item, border=1)
            self.ln()


file_path = 'C:\\Users\\Administrator\\Desktop\\test.pdf'

if os.path.exists(file_path):
    os.remove(file_path)

ReportInfoExporter().generate_pdf(file_path)
