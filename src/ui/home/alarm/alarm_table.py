from common.const_alarm_type import AlarmType
from ui.common.abstract_table import AbstractTable
from db.models.alarm_log import AlarmLog
from common.global_data import gdata


class AlarmTable(AbstractTable):
    def __init__(self):
        super().__init__()
        self.show_checkbox_column = True
        self.table_width = gdata.default_table_width

    def load_total(self):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        sql = AlarmLog.select()
        if start_date and end_date:
            sql = sql.where(AlarmLog.utc_date_time >= start_date,
                            AlarmLog.utc_date_time <= end_date)

        return sql.count()

    def get_event_name(self, alarm_type: int) -> str:
        session = self.page.session
        match alarm_type:
            case AlarmType.PLC_DISCONNECTED:
                return session.get("lang.alarm.plc_disconnected")
            case AlarmType.GPS_DISCONNECTED:
                return session.get("lang.alarm.gps_disconnected")
            case AlarmType.SPS1_DISCONNECTED:
                return session.get("lang.alarm.sps1_disconnected")
            case AlarmType.SPS2_DISCONNECTED:
                return session.get("lang.alarm.sps2_disconnected")
            case AlarmType.APP_UNEXPECTED_EXIT:
                return session.get("lang.alarm.app_unexpected_exit")
            case AlarmType.POWER_OVERLOAD:
                return session.get("lang.alarm.power_overload")
            case _:
                return session.get("lang.alarm.unknown")

    def load_data(self):
        sql = AlarmLog.select(
            AlarmLog.id,
            AlarmLog.utc_date_time,
            AlarmLog.alarm_type,
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
                self.get_event_name(item.alarm_type),
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
