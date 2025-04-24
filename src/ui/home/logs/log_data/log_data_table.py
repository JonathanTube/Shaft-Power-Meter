from db.models.data_log import DataLog
from ui.common.abstract_table import AbstractTable
from common.global_data import gdata


class LogDataTable(AbstractTable):
    def __init__(self):
        super().__init__()
        self.table_width = gdata.default_table_width

    def load_total(self):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        sql = DataLog.select()
        if start_date and end_date:
            sql = sql.where(DataLog.utc_date_time >= start_date, DataLog.utc_date_time <= end_date)

        return sql.count()

    def load_data(self):
        sql = DataLog.select(
            DataLog.id,
            DataLog.name,
            DataLog.utc_date_time,
            DataLog.speed,
            DataLog.thrust,
            DataLog.torque,
            DataLog.power
        )
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        if start_date and end_date:
            sql = sql.where(DataLog.utc_date_time >= start_date,
                            DataLog.utc_date_time <= end_date)

        data = sql.order_by(DataLog.id.desc()).paginate(
            self.current_page, self.page_size)

        return [[
                item.id,
                item.name,
                item.utc_date_time,
                item.speed,
                item.thrust,
                item.torque,
                item.power
                ] for item in data]

    def create_columns(self):
        return self.get_columns()

    def get_columns(self):
        session = self.page.session
        return [
            session.get("lang.common.no"),
            session.get("lang.common.propeller_name"),
            session.get("lang.common.utc_date_time"),
            session.get("lang.common.speed"),
            session.get("lang.common.thrust"),
            session.get("lang.common.torque"),
            session.get("lang.common.power")
        ]

    def before_update(self):
        self.update_columns(self.get_columns())
