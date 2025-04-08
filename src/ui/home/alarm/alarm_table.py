
from ui.common.abstract_table import AbstractTable
from db.models.alarm_log import AlarmLog


class AlarmTable(AbstractTable):

    def load_total(self):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        sql = AlarmLog.select()
        if start_date and end_date:
            sql = sql.where(AlarmLog.utc_date_time >= start_date,
                            AlarmLog.utc_date_time <= end_date)

        return sql.count()

    def load_data(self):
        sql = AlarmLog.select(
            AlarmLog.id,
            AlarmLog.utc_date_time,
            AlarmLog.event_name,
            AlarmLog.acknowledge_time
        )
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        if start_date and end_date:
            sql = sql.where(AlarmLog.utc_date_time >= start_date,
                            AlarmLog.utc_date_time <= end_date)
        data = sql.order_by(AlarmLog.id.desc()).paginate(
            self.current_page, self.page_size)

        return [
            [
                item.id,
                item.utc_date_time,
                item.event_name,
                item.acknowledge_time
            ] for item in data
        ]

    def create_columns(self):
        return self.get_columns()

    def get_columns(self):
        session = self.page.session
        return [
            session.get("lang.common.no"),
            session.get("lang.common.utc_date_time"),
            session.get("lang.common.event_name"),
            session.get("lang.common.acknowledge_time")
        ]

    def before_update(self):
        self.update_columns(self.get_columns())
