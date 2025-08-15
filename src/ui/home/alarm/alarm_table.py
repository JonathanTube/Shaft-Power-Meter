import logging
import flet as ft
from ui.common.abstract_table import AbstractTable
from db.models.alarm_log import AlarmLog
from common.global_data import gdata
from ui.home.alarm.alarm_util import AlarmUtil
from utils.datetime_util import DateTimeUtil
from peewee import fn


class AlarmTable(AbstractTable):
    def __init__(self):
        super().__init__()
        self.show_checkbox_column = True
        self.table_width = gdata.configCommon.default_table_width

    def load_total(self):
        try:
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')

            query = AlarmLog.select(fn.COUNT(AlarmLog.id))
            if start_date and end_date:
                query = query.where(
                    (AlarmLog.utc_date_time >= start_date) &
                    (AlarmLog.utc_date_time <= end_date)
                )

            return query.scalar() or 0  # scalar() 直接返回 count 数字
        except:
            logging.exception("exception occured at AlarmTable.load_total")
            return 0

    def load_data(self):
        try:
            sql = AlarmLog.select(
                AlarmLog.id,
                AlarmLog.alarm_type,
                AlarmLog.occured_time,
                AlarmLog.recovery_time,
                AlarmLog.acknowledge_time,
            )
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')
            if start_date and end_date:
                sql = sql.where(AlarmLog.occured_time >= start_date, AlarmLog.occured_time <= end_date)
            data: list[AlarmLog] = sql.order_by(AlarmLog.id.desc()).paginate(self.current_page, self.page_size)

            data_list = []

            date_time_format = f"{gdata.configDateTime.date_format} %H:%M:%S"
            for item in data:
                recovery_block = "⚠️"
                if item.recovery_time:
                    recovery_block = DateTimeUtil.format_date(item.recovery_time, date_time_format)

                data_list.append([
                    item.id,
                    AlarmUtil.get_event_name(self.page, item.alarm_type),
                    DateTimeUtil.format_date(item.occured_time, date_time_format),
                    recovery_block,
                    DateTimeUtil.format_date(item.acknowledge_time, date_time_format)
                ])

            return data_list
        except:
            logging.exception("exception occured at AlarmTable.load_data")

        return []

    def has_operations(self):
        return False

    def create_columns(self):
        return self.get_columns()

    def get_columns(self):
        try:
            session = self.page.session
            return [
                session.get("lang.common.no"),
                session.get("lang.common.event_name"),
                session.get("lang.alarm.occured_time"),
                session.get("lang.alarm.recovery_time"),
                session.get("lang.common.acknowledge_time")
            ]
        except:
            logging.exception("exception occured at AlarmTable.get_columns")

        return [
            '', '', '', '', ''
        ]
