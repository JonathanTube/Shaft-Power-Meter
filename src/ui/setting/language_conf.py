import flet as ft
from db.models.language import Language
# I need to create a language conf page, which can change the language of the app.
# The language can be changed to Chinese, English
# The default language is English.
# The language is stored in the database, table name is language, field name is code, chinese, english
# I need to modify the chinese and english of the language in the database


class LanguageConf(ft.Container):
    def __init__(self):
        super().__init__()

    def load_total(self):
        return Language.select().count()

    def load_data(self):
        data = Language.select(
            Language.id,
            Language.english,
            Language.chinese
        ).order_by(ReportInfo.id.desc()).paginate(self.current_page, self.page_size)

        # get start_date and end_date from kwargs
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')

        data = []
        if start_date is not None and end_date is not None:
            data = ReportInfo.select(
                ReportInfo.id,
                ReportInfo.report_name,
                ReportInfo.created_at
            ).where(
                ReportInfo.created_at.between(start_date, end_date)
            ).order_by(ReportInfo.id.desc()).paginate(self.current_page, self.page_size)

        else:
            data = ReportInfo.select(
                ReportInfo.id,
                ReportInfo.report_name,
                ReportInfo.created_at
            ).order_by(ReportInfo.id.desc()).paginate(self.current_page, self.page_size)

        return [[item.id, item.report_name, item.created_at] for item in data]

    def has_operations(self):
        return True

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
