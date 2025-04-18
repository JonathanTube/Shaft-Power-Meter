import flet as ft

from ui.common.abstract_table import AbstractTable
from db.models.report_info import ReportInfo
from ui.common.toast import Toast
from ui.report.report_info_detail import ReportInfoDialog
from ui.report.report_info_exporter import ReportInfoExporter


class ReportInfoTable(AbstractTable):
    def __init__(self, page_size: int = 10):
        super().__init__(page_size)
        self.width = 1000

    def load_total(self):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')

        sql = ReportInfo.select()
        if start_date and end_date:
            sql = sql.where(
                ReportInfo.created_at >= start_date,
                ReportInfo.created_at <= end_date
            )
        return sql.count()

    def load_data(self):
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

        return [[item.id, item.report_name, item.created_at] for item in data]

    def has_operations(self):
        return True

    def create_operations(self, items: list):
        view_button = ft.TextButton(
                    icon=ft.Icons.VISIBILITY_OUTLINED,
                    text="View",
                    on_click=lambda e: self.__view_report(e, items[0],items[1])
                )
         
        export_button = ft.TextButton(
                    icon=ft.Icons.DOWNLOAD_OUTLINED,
                    text="Export",
                    on_click=lambda e: self.__export_report(e, items[0],items[1])
                )   

        session = self.page.session
        view_button.text = session.get("lang.common.view")
        export_button.text = session.get("lang.common.export")

        return ft.Row(controls=[view_button, export_button])

    def __view_report(self, e, id: int, report_name: str):
        e.page.open(ReportInfoDialog(id, report_name))

    def __export_report(self, e, id: int, report_name: str):
        file_picker = e.page.session.get('file_picker_for_pdf_export')
        file_picker.save_file(
            file_name=f"{report_name}.pdf",
            allowed_extensions=["pdf"]
        )
        file_picker.on_result = lambda e: self.__on_result(e, id)

    def __on_result(self, e: ft.FilePickerResultEvent, id: int):
        if e.path:
            ReportInfoExporter().generate_pdf(e.path, id)
            Toast.show_success(e.page, self.page.session.get("lang.report.export_success"))

    def create_columns(self):
        return self.__get_language()

    def __get_language(self):
        session = self.page.session
        return [
            session.get("lang.common.no"),
            session.get("lang.report.report_name"),
            session.get("lang.common.created_at")
        ]

    def before_update(self):
        self.update_columns(self.__get_language())
