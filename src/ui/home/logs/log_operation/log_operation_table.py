from db.models.opearation_log import OperationLog
from ui.common.abstract_table import AbstractTable


class LogOperationTable(AbstractTable):

    def load_total(self):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        sql = OperationLog.select()
        if start_date and end_date:
            sql = sql.where(OperationLog.utc_date_time >= start_date, OperationLog.utc_date_time <= end_date)

        return sql.count()

    def load_data(self):
        sql = OperationLog.select(
            OperationLog.id,
            OperationLog.utc_date_time,
            OperationLog.operation_type,
            OperationLog.operation_content
        )
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        if start_date and end_date:
            sql = sql.where(OperationLog.utc_date_time >= start_date, OperationLog.utc_date_time <= end_date)
        data: list[OperationLog] = sql.order_by(OperationLog.id.desc()).paginate(self.current_page, self.page_size)

        return [
            [
                item.id,
                item.utc_date_time,
                item.operation_type,
                item.operation_content
            ] for item in data
        ]

    def create_columns(self):
        return self.get_columns()

    def get_columns(self):
        session = self.page.session
        return [
            session.get("lang.common.no"),
            session.get("lang.common.utc_date_time"),
            session.get("lang.operation_log.operation_type"),
            session.get("lang.operation_log.operation_content")
        ]

    def before_update(self):
        self.update_columns(self.get_columns())
