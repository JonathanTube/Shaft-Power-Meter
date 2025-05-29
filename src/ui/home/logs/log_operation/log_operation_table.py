from db.models.operation_log import OperationLog
from db.models.date_time_conf import DateTimeConf
from common.operation_type import OperationType
from ui.common.abstract_table import AbstractTable
from common.global_data import gdata


class LogOperationTable(AbstractTable):
    def __init__(self):
        super().__init__()
        self.table_width = gdata.default_table_width
        self.dtc: DateTimeConf = DateTimeConf.get()

    def load_total(self):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        operation_type = self.kwargs.get('operation_type')
        sql = OperationLog.select()
        if start_date and end_date:
            sql = sql.where(OperationLog.utc_date_time >= start_date, OperationLog.utc_date_time <= end_date)
        if operation_type != -1 or operation_type != None:
            sql = sql.where(OperationLog.operation_type == operation_type)

        cnt = sql.count()
        if cnt > 0:
            self.table_width = None
        return cnt

    def load_data(self):
        sql = OperationLog.select(
            OperationLog.id,
            OperationLog.utc_date_time,
            OperationLog.operation_type,
            OperationLog.operation_content
        )
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        operation_type = self.kwargs.get('operation_type')
        if start_date and end_date:
            sql = sql.where(OperationLog.utc_date_time >= start_date, OperationLog.utc_date_time <= end_date)
        if operation_type != -1 and operation_type != None:
            sql = sql.where(OperationLog.operation_type == operation_type)
        data: list[OperationLog] = sql.order_by(OperationLog.id.desc()).paginate(self.current_page, self.page_size)

        return [
            [
                item.id,
                item.utc_date_time.strftime(f'{self.dtc.date_format} %H:%M:%S'),
                OperationType.get_operation_type_name(item.operation_type),
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
