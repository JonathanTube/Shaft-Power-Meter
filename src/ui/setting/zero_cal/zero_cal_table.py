from db.models.zero_cal_info import ZeroCalInfo
from ui.common.abstract_table import AbstractTable
from common.global_data import gdata
from db.models.date_time_conf import DateTimeConf


class ZeroCalTable(AbstractTable):
    def __init__(self):
        super().__init__()
        self.table_width = gdata.default_table_width - 160
        self.dtc: DateTimeConf = DateTimeConf.get()

    def load_total(self):
        try:
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')
            sql = ZeroCalInfo.select()
            if start_date and end_date:
                sql = sql.where(ZeroCalInfo.utc_date_time >=
                                start_date, ZeroCalInfo.utc_date_time <= end_date)

            return sql.count()
        except:
            return 0

    def load_data(self):
        try:
            sql = ZeroCalInfo.select(
                ZeroCalInfo.id,
                ZeroCalInfo.name,
                ZeroCalInfo.utc_date_time,
                ZeroCalInfo.torque_offset,
                ZeroCalInfo.thrust_offset
            )
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')
            if start_date and end_date:
                sql = sql.where(ZeroCalInfo.utc_date_time >= start_date, ZeroCalInfo.utc_date_time <= end_date)
            data = sql.order_by(ZeroCalInfo.id.desc()).paginate(
                self.current_page, self.page_size)

            return [
                [
                    item.id,
                    item.name,
                    item.utc_date_time.strftime(
                        f'{self.dtc.date_format} %H:%M:%S'),
                    round(item.torque_offset, 10) if item.torque_offset else 0,
                    round(item.thrust_offset, 10) if item.thrust_offset else 0
                ] for item in data
            ]
        except:
            return []

    def create_columns(self):
        return self.get_columns()

    def get_columns(self):
        if self.page and self.page.session:
            session = self.page.session
            return [
                session.get("lang.common.no"),
                session.get("lang.zero_cal.name"),
                session.get("lang.common.utc_date_time"),
                session.get("lang.zero_cal.torque_offset"),
                session.get("lang.zero_cal.thrust_offset")
            ]
        
        return []