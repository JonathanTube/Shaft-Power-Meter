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
                item.utc_date,
                item.utc_time,
                item.revolution,
                item.thrust,
                item.torque,
                item.power
                ] for item in data]

    @override
    def create_columns(self):
        return [
            "No.",
            "Name",
            "UTC Date",
            "UTC Time",
            "Revolution(Rev/Min)",
            "Thrust(kN)",
            "Torque(kNm)",
            "Power(kW)"
        ]
