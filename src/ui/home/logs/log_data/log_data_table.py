from typing import override

from db.models.data_log import DataLog
from ui.common.abstract_table import AbstractTable


class LogDataTable(AbstractTable):
    @override
    def load_total(self):
        return DataLog.select().count()

    @override
    def load_data(self):
        data = DataLog.select(
            DataLog.id,
            DataLog.name,
            DataLog.utc_date,
            DataLog.utc_time,
            DataLog.revolution,
            DataLog.thrust,
            DataLog.torque,
            DataLog.power
        ).order_by(DataLog.id.desc()).paginate(self.current_page, self.page_size)

        return [[
                item.id,
                item.name,
                f'{item.utc_date} {item.utc_time}',
                item.revolution,
                item.thrust,
                item.torque,
                item.power
                ] for item in data]

    @override
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
