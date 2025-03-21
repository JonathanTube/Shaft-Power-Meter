from typing import override
import flet as ft

from ui.common.abstract_table import AbstractTable
from db.models.report_info import ReportInfo
from ui.common.toast import Toast
from ui.report.report_info_detail import ReportInfoDialog
from ui.report.report_info_exporter import ReportInfoExporter


class ReportInfoTable(AbstractTable):
    @override
    def load_total(self):
        # get start_date and end_date from kwargs
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')

        if start_date and end_date:
            return ReportInfo.select().where(
                ReportInfo.created_at.between(start_date, end_date)
            ).count()

        return ReportInfo.select().count()

    @override
    def load_data(self):
        query = ReportInfo.select(
            ReportInfo.id,
            ReportInfo.report_name,
            ReportInfo.created_at
        ).order_by(ReportInfo.id.desc()).paginate(self.current_page, self.page_size)

        # get start_date and end_date from kwargs
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')

        if start_date and end_date:
            query = query.where(
                ReportInfo.created_at.between(start_date, end_date)
            )

        data = query.execute()

        return [[item.id, item.report_name, item.created_at] for item in data]

    @override
    def create_columns(self):
        return ["No.", "Report Name", "Create At"]

    @override
    def has_operations(self):
        return True

    @override
    def create_operations(self, _id: int):
        return ft.Row(
            controls=[
                ft.TextButton(
                    icon=ft.Icons.VISIBILITY_OUTLINED,
                    text="View",
                    on_click=lambda e: self.__view_report(e, _id)
                ),
                ft.TextButton(
                    icon=ft.Icons.DOWNLOAD_OUTLINED,
                    text="Export",
                    on_click=lambda e: self.__export_report(e, _id)
                )
            ])

    def __view_report(self, e, _id: str):
        e.page.open(ReportInfoDialog(_id))

    def __export_report(self, e, _id):
        self.id = _id
        file_picker = e.page.session.get('file_picker_for_pdf_export')
        file_picker.save_file(
            file_name="report.pdf",
            allowed_extensions=["pdf"]
        )
        file_picker.on_result = self.__on_result

    def __on_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            ReportInfoExporter().generate_pdf(e.path)
            Toast.show_success(e.page, "export success")
