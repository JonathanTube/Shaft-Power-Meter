from fpdf import FPDF


class ReportInfoExporter(FPDF):
    def __init__(self):
        super().__init__()
        self.per_cell_width = 47.5
        self.add_page()

    def generate_pdf(self, path, id: int):
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
        self.__insert_value("Chemical Tanker", w=self.per_cell_width)
        self.__insert_label("IMO Number", w=self.per_cell_width)
        self.__insert_value("IMO9856724", w=self.per_cell_width)
        self.ln()

        self.__insert_label("Ship Size(DWT)", w=self.per_cell_width)
        self.__insert_value("50,000 MT", w=self.per_cell_width)
        self.__insert_label("Ship Name", w=self.per_cell_width)
        self.__insert_value("Blue Ocean", w=self.per_cell_width)
        self.ln()

        self.__insert_label("Un-limited Power", w=self.per_cell_width)
        self.__insert_value("15,000 kW", w=self.per_cell_width)
        self.__insert_label("Limited Power", w=self.per_cell_width)
        self.__insert_value("12,000 kW", w=self.per_cell_width)
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
        self.set_text_color(66, 66, 66)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, item, border=1)
            self.ln()

    def __handle_event_log_start(self):
        label_width = self.per_cell_width * 2
        value_width = self.per_cell_width * 2
        self.__insert_label("Date/Time of Power Reserve Breach", w=label_width)
        self.__insert_value("2025-03-20 14:30 UTC", w=value_width)
        self.ln()

        self.__insert_label(
            "Ship position of power reserve breach", w=label_width)
        self.__insert_value("35°12'N 139°46'E", w=value_width)
        self.ln()

        self.__insert_label("Beaufort number", w=label_width)
        self.__insert_value("6", w=value_width)
        self.ln()

        self.__insert_label("Wave height", w=label_width)
        self.__insert_value("4.2 m", w=value_width)
        self.ln()

        self.__insert_label("Ice condition", w=label_width)
        self.__insert_value("None", w=value_width)
        self.ln()

        self.__insert_label("Reason for reserve usage", w=label_width)
        self.__insert_value("Storm avoidance", w=value_width)
        self.ln()

        self.__insert_horizontal_line()

    def __handle_event_log_end(self):
        label_width = self.per_cell_width * 2
        value_width = self.per_cell_width * 2
        self.__insert_label(
            "Date/Time when returning to limited power", w=label_width)
        self.__insert_value("2025-03-20 16:45 UTC", w=value_width)
        self.ln()

        self.__insert_label(
            "Ship position when returning to limited power", w=label_width)
        self.__insert_value("36°05'N 140°12'E", w=value_width)
        self.ln()

        self.__insert_label("Beaufort number", w=label_width)
        self.__insert_value("4", w=value_width)
        self.ln()

        self.__insert_label("Wave height", w=label_width)
        self.__insert_value("2.1 m", w=value_width)
        self.ln()

        self.__insert_label("Ice condition", w=label_width)
        self.__insert_value("None", w=value_width)
        self.ln()

        self.__insert_label("Reason for reserve usage", w=label_width)
        self.__insert_value("Storm avoidance", w=value_width)
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
