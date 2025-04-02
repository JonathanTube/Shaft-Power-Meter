from db.models.gps_log import GpsLog
from ui.common.abstract_table import AbstractTable


class LogGpsTable(AbstractTable):

    def load_total(self):
        return GpsLog.select().count()


    def load_data(self):
        data = GpsLog.select(
            GpsLog.id,
            GpsLog.utc_date,
            GpsLog.utc_time,
            GpsLog.longitude,
            GpsLog.latitude
        ).order_by(GpsLog.id.desc()).paginate(self.current_page, self.page_size)

        return [
            [
                item.id,
                f'{item.utc_date} {item.utc_time}',
                f'{item.longitude} {item.latitude}'
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

    def before_update(self):
        self.update_columns(self.get_columns())
