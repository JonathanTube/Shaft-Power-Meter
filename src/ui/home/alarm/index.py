import asyncio
import logging
import flet as ft
import pandas as pd
import random
import string
from db.models.alarm_log import AlarmLog
from ui.common.datetime_search import DatetimeSearch
from ui.common.toast import Toast
from ui.home.alarm.alarm_table import AlarmTable
from common.global_data import gdata
from common.const_alarm_type import AlarmType


class AlarmList(ft.Container):
    def __init__(self):
        super().__init__()
        self.file_picker = None
        self.expand = True
        self.padding = 10
        self.table = None

        self.task_running = False

    def build(self):
        self.search = DatetimeSearch(self.__on_search)
        export_button = ft.OutlinedButton(text=self.page.session.get("lang.common.export"), height=40, icon=ft.Icons.DOWNLOAD_OUTLINED, on_click=self.__on_export)

        self.table = AlarmTable()

        ack_button = ft.OutlinedButton(text=self.page.session.get("lang.alarm.acknowledge"), height=40, icon=ft.Icons.CHECK_CIRCLE_OUTLINED, on_click=self.__on_acknowledge)

        self.content = ft.Column(
            expand=False,
            spacing=5,
            controls=[
                ft.Row([self.search, export_button, ack_button]),
                self.table
            ]
        )

    def __on_export(self, e):
        self.file_picker = ft.FilePicker()
        self.page.overlay.append(self.file_picker)
        self.page.update()
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
        self.file_picker.save_file(file_name=f"AlarmLog_{random_str}.xlsx", allowed_extensions=["xlsx", "xls"])
        self.file_picker.on_result = lambda e: self.__on_result(e)

    def __on_result(self, e):
        if e.path:
            start_date = self.search.date_time_range.start_date.value
            end_date = self.search.date_time_range.end_date.value
            if start_date and end_date:
                query = AlarmLog.select(
                    AlarmLog.utc_date_time,
                    AlarmLog.alarm_type, AlarmLog.acknowledge_time
                ).where(
                    AlarmLog.utc_date_time >= start_date,
                    AlarmLog.utc_date_time <= end_date
                ).order_by(AlarmLog.id.desc()).limit(1000)
            else:
                query = AlarmLog.select(
                    AlarmLog.utc_date_time,
                    AlarmLog.alarm_type,
                    AlarmLog.acknowledge_time
                ).order_by(AlarmLog.id.desc()).limit(1000)
            data = []
            for item in query:
                data.append({
                    "utc_date_time": item.utc_date_time,
                    "alarm_type": AlarmType.get_alarm_type_name(item.alarm_type),
                    "acknowledge_time": item.acknowledge_time
                })
            df = pd.DataFrame(data)
            with pd.ExcelWriter(e.path, engine="xlsxwriter") as writer:  # 显式指定引擎
                df.to_excel(writer, sheet_name="Alarm Log", index=False)
                # 获取工作表对象
                worksheet = writer.sheets["Alarm Log"]
                # 精确设置列宽（通过列位置索引）
                column_width_config = {
                    0: 30,   # 第一列（时间列）宽度：22字符
                    1: 40,   # 第二列（报警类型）宽度：25
                    2: 30    # 第三列（确认时间）宽度：20
                }
                # 批量设置列宽
                for col_num, width in column_width_config.items():
                    worksheet.set_column(col_num, col_num, width)
                # 如果需要设置日期格式（额外优化）
                date_format = writer.book.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
                worksheet.set_column(0, 0, 22, date_format)  # 重新设置第一列格式

        if self.file_picker:
            self.page.overlay.remove(self.file_picker)

    def __on_acknowledge(self, e):
        # get selected rows
        selected_rows = [item for item in self.table.data_table.rows if item.selected]
        if len(selected_rows) == 0:
            Toast.show_error(self.page, self.page.session.get("lang.alarm.please_select_at_least_one_alarm"))
            return

        for row in selected_rows:
            AlarmLog.update(acknowledge_time=gdata.utc_date_time).where(AlarmLog.id == row.cells[0].data).execute()

        self.table.search()
        Toast.show_success(self.page)

    def __on_search(self, start_date: str, end_date: str):
        self.table.search(start_date=start_date, end_date=end_date)

    async def __loop(self, table : AlarmTable):
        while self.task_running:
            try:
                selected_rows = [item for item in table.data_table.rows if item.selected]
                # 只有当没有选中复选框的时候
                if len(selected_rows) == 0:
                    # 才去更新表格
                    if self.table and self.table.page:
                        self.table.search()
            except:
                logging.exception("exception occured at AlarmList")
            finally:
                await asyncio.sleep(5)
    
    def did_mount(self):
        self.task_running = True
        self.__task = self.page.run_task(self.__loop, self.table)

    def will_unmount(self):
        self.task_running = False
        if self.__task:
            self.__task.cancel()