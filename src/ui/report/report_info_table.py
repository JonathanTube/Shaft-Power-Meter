import logging
import flet as ft

from peewee import fn
from ui.common.abstract_table import AbstractTable
from db.models.report_info import ReportInfo
from ui.common.toast import Toast
from ui.report.report_info_detail import ReportInfoDialog
from ui.report.report_info_exporter import ReportInfoExporter
from common.global_data import gdata
from db.models.date_time_conf import DateTimeConf

class ReportInfoTable(AbstractTable):
    def __init__(self):
        super().__init__()
        self.file_picker = None
        self.table_width = gdata.configCommon.default_table_width

        datetime_conf: DateTimeConf = DateTimeConf.get()
        date_format = datetime_conf.date_format
        self.date_time_format = f"{date_format} %H:%M:%S"

    def load_total(self):
        try:
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')

            query = ReportInfo.select(fn.COUNT(ReportInfo.id))

            if start_date:
                query = query.where(ReportInfo.created_at >= start_date)
            if end_date:
                query = query.where(ReportInfo.created_at <= end_date)

            return query.scalar() or 0
        except:
            logging.exception('exception occured at ReportInfoTable.load_total')

        return 0

    def load_data(self):
        try:
            sql = ReportInfo.select(
                ReportInfo.id,
                ReportInfo.report_name,
                ReportInfo.created_at
            )
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')
            if start_date and end_date:
                sql = sql.where(
                    ReportInfo.created_at >= start_date,
                    ReportInfo.created_at <= end_date
                )

            data = sql.order_by(ReportInfo.id.desc()).paginate(
                self.current_page, self.page_size)

            return [[item.id, item.report_name, item.created_at.strftime(self.date_time_format)] for item in data]
        except:
            logging.exception('exception occured at ReportInfoTable.load_data')

        return []

    def has_operations(self):
        return True

    def create_operations(self, items: list):
        try:
            view_button = ft.TextButton(
                icon=ft.Icons.VISIBILITY_OUTLINED,
                text="View",
                on_click=lambda e: self.__view_report(e, items[0], items[1])
            )

            export_button = ft.TextButton(
                icon=ft.Icons.DOWNLOAD_OUTLINED,
                text="Export",
                on_click=lambda e: self.__export_report(e, items[0], items[1])
            )

            if self.page and self.page.session:
                session = self.page.session
                view_button.text = session.get("lang.common.view")
                export_button.text = session.get("lang.common.export")

            return ft.Row(controls=[view_button, export_button])
        except:
            logging.exception('exception occured at ReportInfoTable.create_operations')

        return ft.Row(controls=[])

    def __view_report(self, e, id: int, report_name: str):
        try:
            if self.page is not None:
                self.page.open(ReportInfoDialog(id, report_name))
        except:
            logging.exception('exception occured at ReportInfoTable.__view_report')

    def __export_report(self, e, id: int, report_name: str):
        try:
            if self.page and self.page.overlay:
                self.file_picker = ft.FilePicker()
                self.page.overlay.append(self.file_picker)
                self.page.update()
                self.file_picker.save_file(file_name=f"{report_name}.pdf", allowed_extensions=["pdf"])
                self.file_picker.on_result = lambda e: self.__on_result(e, id)
        except:
            logging.exception('exception occured at ReportInfoTable.__export_report')

    def __on_result(self, e: ft.FilePickerResultEvent, id: int):
        try:
            if self.page is None or self.page.session is None:
                return

            if e.path:
                ReportInfoExporter().generate_pdf(e.path, id)
                Toast.show_success(e.page, self.page.session.get("lang.report.export_success"))

            if self.file_picker is None or self.file_picker.page is None:
                return

            if self.page.overlay is None:
                return

            if self.file_picker in self.page.overlay:
                self.page.overlay.remove(self.file_picker)
        except:
            logging.exception('exception occured at ReportInfoTable.__on_result')

    def create_columns(self):
        return self.__get_language()

    def __get_language(self):
        try:
            if self.page and self.page.session:
                session = self.page.session
                return [
                    session.get("lang.common.no"),
                    session.get("lang.report.report_name"),
                    session.get("lang.common.created_at")
                ]
        except:
            logging.exception('exception occured at ReportInfoTable.__on_result')

        return ["", "", ""]
