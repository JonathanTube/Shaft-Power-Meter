import logging
from db.models.data_log import DataLog
from ui.common.abstract_table import AbstractTable
from common.global_data import gdata
from db.models.date_time_conf import DateTimeConf
from utils.unit_parser import UnitParser
from peewee import fn


class LogDataTable(AbstractTable):
    def __init__(self):
        super().__init__()
        self.table_width = gdata.configCommon.default_table_width
        self.dtc: DateTimeConf = DateTimeConf.get()

    def load_total(self):
        try:
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')

            query = DataLog.select(fn.COUNT(DataLog.id))

            if start_date and end_date:
                query = query.where(
                    (DataLog.utc_date_time >= start_date) &
                    (DataLog.utc_date_time <= end_date)
                )

            return query.scalar() or 0
        except:
            logging.exception('exception occurred at LogDataTable.load_total')
            return 0

    def load_data(self):
        try:
            sql = DataLog.select(
                DataLog.id,
                DataLog.name,
                DataLog.utc_date_time,
                DataLog.ad_0_torque,
                DataLog.ad_1_thrust,
                DataLog.speed,
                DataLog.power
            )
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')
            if start_date and end_date:
                sql = sql.where(DataLog.utc_date_time >= start_date,
                                DataLog.utc_date_time <= end_date)

            data = sql.order_by(DataLog.id.desc()).paginate(self.current_page, self.page_size)

            data_list = []
            for item in data:
                torque = UnitParser.parse_torque(item.ad_0_torque, 0)
                thrust = UnitParser.parse_thrust(item.ad_1_thrust, 0)
                power = UnitParser.parse_power(item.power, 0)
                speed = UnitParser.parse_speed(item.speed)
                data_list.append([
                    item.id,
                    item.name,
                    item.utc_date_time.strftime(f'{self.dtc.date_format} %H:%M:%S'),
                    torque[0],
                    thrust[0],
                    speed[0],
                    power[0]
                ])

            return data_list
        except:
            logging.exception('exception occured at LogDataTable.load_data')

        return []

    def create_columns(self):
        return self.get_columns()

    def get_columns(self):
        try:
            if self.page is None:
                return []

            if self.page.session is None:
                return []

            session = self.page.session
            return [
                session.get("lang.common.no"),
                session.get("lang.common.propeller_name"),
                session.get("lang.common.utc_date_time"),
                f'{session.get("lang.common.torque")}(kNm)',
                f'{session.get("lang.common.thrust")}(kN)',
                f'{session.get("lang.common.speed")}(rpm)',
                f'{session.get("lang.common.power")}(kW)'
            ]
        except:
            logging.exception('exception occured at LogDataTable.get_columns')

        return []
