import logging
from common.const_alarm_type import AlarmType
from ui.common.abstract_table import AbstractTable
from db.models.alarm_log import AlarmLog
from common.global_data import gdata
from db.models.date_time_conf import DateTimeConf


class AlarmTable(AbstractTable):
    def __init__(self):
        super().__init__()

        datetime_conf: DateTimeConf = DateTimeConf.get()
        date_format = datetime_conf.date_format
        self.date_time_format = f"{date_format} %H:%M:%S"

        self.show_checkbox_column = True
        self.table_width = gdata.default_table_width

    def load_total(self):
        try:
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')
            sql = AlarmLog.select()
            if start_date and end_date:
                sql = sql.where(AlarmLog.utc_date_time >= start_date, AlarmLog.utc_date_time <= end_date)

            return sql.count()
        except:
            logging.exception("exception occured at AlarmTable.load_total")

        return 0

    def get_event_name(self, alarm_type: int) -> str:
        try:
            if self.page is None or self.page.session is None:
                return ''

            session = self.page.session
            match alarm_type:
                case AlarmType.MASTER_PLC_DISCONNECTED:
                    return session.get("lang.alarm.master_plc_disconnected")
                case AlarmType.SLAVE_GPS_DISCONNECTED:
                    return session.get("lang.alarm.slave_gps_disconnected")
                case AlarmType.MASTER_GPS_DISCONNECTED:
                    return session.get("lang.alarm.master_gps_disconnected")
                case AlarmType.MASTER_SPS1_DISCONNECTED:
                    return session.get("lang.alarm.master_sps1_disconnected")
                case AlarmType.MASTER_SPS2_DISCONNECTED:
                    return session.get("lang.alarm.master_sps2_disconnected")
                case AlarmType.MASTER_SERVER_STOPPED:
                    return session.get("lang.alarm.master_server_stopped")
                case AlarmType.SLAVE_CLIENT_DISCONNECTED:
                    return session.get("lang.alarm.slave_master_disconnected")
                case AlarmType.APP_UNEXPECTED_EXIT:
                    return session.get("lang.alarm.app_unexpected_exit")
                case AlarmType.POWER_OVERLOAD:
                    return session.get("lang.alarm.power_overload")
                case _:
                    return session.get("lang.alarm.unknown")
        except:
            logging.exception("exception occured at AlarmTable.get_event_name")

        return ''

    def load_data(self):
        try:
            sql = AlarmLog.select(
                AlarmLog.id,
                AlarmLog.utc_date_time,
                AlarmLog.alarm_type,
                AlarmLog.acknowledge_time,
                AlarmLog.is_recovery,
                AlarmLog.is_from_master
            )
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')
            if start_date and end_date:
                sql = sql.where(AlarmLog.utc_date_time >= start_date, AlarmLog.utc_date_time <= end_date)
            data: list[AlarmLog] = sql.order_by(AlarmLog.id.desc()).paginate(self.current_page, self.page_size)

            data_list = []

            for item in data:
                status_column = '✔️'if item.is_recovery else '❌'
                if item.is_from_master != gdata.is_master:
                    status_column += '🔒'

                data_list.append([
                    item.id,
                    item.utc_date_time.strftime(self.date_time_format),
                    self.get_event_name(item.alarm_type),
                    item.acknowledge_time.strftime(self.date_time_format) if item.acknowledge_time else "",
                    status_column
                ])

            return data_list
        except:
            logging.exception("exception occured at AlarmTable.load_data")

        return []

    def create_columns(self):
        return self.get_columns()

    def get_columns(self):
        try:
            session = self.page.session
            return [
                session.get("lang.common.no"),
                session.get("lang.common.utc_date_time"),
                session.get("lang.common.event_name"),
                session.get("lang.common.acknowledge_time"),
                session.get("lang.common.recovery_status")
            ]
        except:
            logging.exception("exception occured at AlarmTable.get_columns")

        return [
            '', '', '', '', ''
        ]
