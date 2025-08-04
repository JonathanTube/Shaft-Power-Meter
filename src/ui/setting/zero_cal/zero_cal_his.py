import logging
import random
import string
import flet as ft
import pandas as pd

from db.models.zero_cal_info import ZeroCalInfo
from ui.common.datetime_search import DatetimeSearch
from ui.setting.zero_cal.zero_cal_table import ZeroCalTable


class ZeroCalHis(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

    def build(self):
        try:
            if self.page and self.page.session:
                self.search = DatetimeSearch(self.__on_search)
                export_button = ft.OutlinedButton(
                    height=40,
                    on_click=self.__on_export,
                    icon=ft.Icons.DOWNLOAD_OUTLINED,
                    text=self.page.session.get("lang.common.export")
                )

                self.table = ZeroCalTable()

                self.content = ft.Column(
                    expand=True,
                    spacing=5,
                    controls=[ft.Row([self.search, export_button]), self.table]
                )
        except:
            logging.exception('exception occured at ZeroCalHis.build')


    def __on_search(self, start_date: str, end_date: str):
        self.table.search(start_date=start_date, end_date=end_date)


    def __on_export(self, e):
        try:
            if self.page is not None:
                self.file_picker = ft.FilePicker()
                self.page.overlay.append(self.file_picker)
                self.page.update()
                random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
                self.file_picker.save_file(file_name=f"Zero_Cal_History_{random_str}.xlsx", allowed_extensions=["xlsx", "xls"])
                self.file_picker.on_result = lambda e: self.__on_result(e)
        except:
            logging.exception('exception occured at ZeroCalHis.__on_export')



    def __on_result(self, e):
        if e.path:
            start_date = self.search.date_time_range.start_date.value
            end_date = self.search.date_time_range.end_date.value
            if start_date and end_date:
                query = ZeroCalInfo.select(
                    ZeroCalInfo.utc_date_time,
                    ZeroCalInfo.torque_offset,
                    ZeroCalInfo.thrust_offset
                ).where(
                    ZeroCalInfo.utc_date_time >= start_date,
                    ZeroCalInfo.utc_date_time <= end_date
                ).order_by(ZeroCalInfo.id.desc()).limit(1000)
            else:
                query = ZeroCalInfo.select(
                    ZeroCalInfo.utc_date_time,
                    ZeroCalInfo.torque_offset,
                    ZeroCalInfo.thrust_offset
                ).order_by(ZeroCalInfo.id.desc()).limit(1000)
            data = []
            for item in query:
                data.append({
                    self.page.session.get("lang.common.utc_date_time"): item.utc_date_time,
                    self.page.session.get("lang.zero_cal.torque_offset"): item.torque_offset,
                    self.page.session.get("lang.zero_cal.thrust_offset"): item.thrust_offset
                })
            df = pd.DataFrame(data)
            with pd.ExcelWriter(e.path, engine="xlsxwriter") as writer:  # 显式指定引擎
                df.to_excel(writer, sheet_name="Zero Cal History", index=False)
                # 获取工作表对象
                worksheet = writer.sheets["Zero Cal History"]
                # 精确设置列宽（通过列位置索引）
                column_width_config = {
                    0: 30,   # 第一列（时间列）宽度：22字符
                    1: 40,   # 第二列（报警类型）宽度：25
                    2: 30,   # 第三列（确认时间）宽度：20
                    3: 30,   # 第四列（确认时间）宽度：20
                    4: 30,   # 第五列（确认时间）宽度：20
                    5: 30    # 第六列（确认时间）宽度：20
                }
                # 批量设置列宽
                for col_num, width in column_width_config.items():
                    worksheet.set_column(col_num, col_num, width)
                # 如果需要设置日期格式（额外优化）
                date_format = writer.book.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
                worksheet.set_column(0, 0, 22, date_format)  # 重新设置第一列格式

        if self.file_picker:
            self.page.overlay.remove(self.file_picker)