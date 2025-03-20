import flet as ft
from fpdf import FPDF
from ui.common.toast import Toast

class ReportInfoExporter(FPDF):
    def __init__(self):
        super().__init__()
        self.path = None

    def export(self, page: ft.Page, _id: str):
        file_picker =page.session.get('file_picker_for_pdf_export')
        file_picker.save_file(
            file_name="report.pdf",
            allowed_extensions=["pdf"]
        )
        file_picker.on_result = self.__on_result

    def __on_result(self,e: ft.FilePickerResultEvent):
        if e.path:
            self.path = e.path
            self.__generate_pdf()
            Toast.show_success(e.page,"success")

    def two_column_row(self, left_label, left_value, right_label="", right_value=""):
        # 计算内容高度
        line_height = 10  # 单行高度

        # 当前Y坐标
        start_y = self.get_y()

        # 计算左边内容的高度
        left_content = f"{left_label}: {left_value}"
        left_width = 90  # 左边列占总宽度的45%
        left_height = self.calc_line_height(left_content, left_width)

        # 计算右边内容的高度（如果有）
        right_height = 0
        right_content = ""
        if right_label:
            right_content = f"{right_label}: {right_value}"
            right_height = self.calc_line_height(right_content, left_width)

        # 取最大高度作为本行高度
        max_height = max(left_height, right_height)

        # 第一列
        self.multi_cell(
            w=left_width,
            h=line_height,
            txt=left_content,
            border=0,
            fill=False
        )

        # 第二列定位
        self.set_xy(left_width + 20, start_y)  # 加上间隔

        # 右侧内容（如果有）
        if right_label:
            self.multi_cell(
                w=left_width,
                h=line_height,
                txt=right_content,
                border=0,
                fill=False
            )

        # 更新Y坐标
        self.set_xy(10, start_y + max_height)

    def calc_line_height(self, text, max_width):
        """计算文本需要的高度"""
        text_width = self.get_string_width(text)
        lines = 1
        current_width = text_width

        # 自动换行计算
        while current_width > max_width:
            lines += 1
            current_width -= max_width

        return lines * 10  # 10为行高

    def __generate_pdf(self):
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

        self.__handle_report_title()

        self.__handle_basic_info()

        self.__handle_event_log()

        self.__handle_data_log()

        self.output(self.path)

    # 设置标题
    def __handle_report_title(self):
        # 设置字体和样式
        self.set_font(family="Arial", size=16)
        # 主标题
        self.cell(200, 10, "Compliance Reporting", ln=1)
        self.ln(5) #下移5mm

    # 第一部分：基本信息
    def __handle_basic_info(self):
        self.set_font(family="Arial", size=12)
        data = [
            ("Ship Type", "Chemical Tanker", "IMO Number", "IMO9856724"),
            ("Ship Size(DWT)", "50,000 MT", "Ship Name", "Blue Ocean"),
            ("Un-limited Power", "15,000 kW", "Limited Power", "12,000 kW")
        ]

        for row in data:
            left_label, left_val, right_label, right_val = row
            self.two_column_row(left_label, left_val, right_label, right_val)

    # 第二部分：ShaPoLi事件日志
    def __handle_event_log(self):
        self.set_font(family="Arial",  size=12)
        self.cell(0, 10, "ShaPoLi Event Log", ln=1)
        event_data = [
            ("Date/Time of Power Reserve Breach:", "2025-03-20 14:30 UTC","Ship position of power reserve breach:", "35°12'N 139°46'E"),
            ("Beaufort number:", "6","Wave height:", "4.2 m"),
            ("Ice condition:", "None", "Reason for reserve usage:", "Storm avoidance"),
            ("Return to limited power datetime:", "2025-03-20 16:45 UTC","Return position:", "36°05'N 140°12'E"),
            ("Return Beaufort number:", "4","Return wave height:", "2.1 m"),
            ("Return ice condition:", "None")
        ]

        for row in event_data:
            self.two_column_row(*row)

    def __handle_data_log(self):
        # 第三部分：数据日志表格
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, "ShaPoLi Data Log", ln=1)

        # 表头
        col_widths = [15, 40, 25, 25, 35, 35]
        headers = ["No.", "Date/Time", "Speed(rpm)", "Torque(kNm)", "Power(kW)", "Total Power(kW)"]

        self.set_fill_color(200, 220, 255)
        self.set_font("Arial", 'B', 10)

        # 绘制表头
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, border=1, fill=True)
        self.ln()

        # 表格数据
        data = [
            ("1", "2025-03-20 14:30", "85", "1200", "4500", "15000"),
            ("2", "2025-03-20 15:00", "82", "1150", "4300", "14800"),
            ("3", "2025-03-20 15:30", "80", "1100", "4100", "14600")
        ]

        self.set_font("Arial", '', 10)
        fill = False
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, item, border=1, fill=fill)
            self.ln()
            fill = not fill