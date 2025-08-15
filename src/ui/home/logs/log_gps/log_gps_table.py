from db.models.gps_log import GpsLog
from ui.common.abstract_table import AbstractTable
from common.global_data import gdata
from peewee import fn


class LogGpsTable(AbstractTable):
    def __init__(self):
        super().__init__()
        self.table_width = gdata.configCommon.default_table_width

    def load_total(self):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')

        query = GpsLog.select(fn.COUNT(GpsLog.id))

        if start_date and end_date:
            query = query.where(
                (GpsLog.utc_date_time >= start_date) &
                (GpsLog.utc_date_time <= end_date)
            )

        return query.scalar()  # 直接返回整数

    def load_data(self):
        sql = GpsLog.select(
            GpsLog.id,
            GpsLog.utc_date_time,
            GpsLog.location
        )
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        if start_date and end_date:
            sql = sql.where(GpsLog.utc_date_time >= start_date,
                            GpsLog.utc_date_time <= end_date)
        data = sql.order_by(GpsLog.id.desc()).paginate(
            self.current_page, self.page_size)

        return [
            [
                item.id,
                item.utc_date_time,
                item.location
            ] for item in data
        ]

    def create_columns(self):
        return self.get_columns()

    def get_columns(self):
        session = self.page.session
        return [
            session.get("lang.common.no"),
            session.get("lang.common.utc_date_time"),
            session.get("lang.common.location")
        ]
