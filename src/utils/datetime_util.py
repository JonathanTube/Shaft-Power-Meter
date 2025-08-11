from datetime import datetime


class DateTimeUtil:
    def parse_date(string: str, default_format: str = '%Y-%m-%d %H:%M:%S') -> datetime:
        if string is None or string == '':
            return None
        return datetime.strptime(string, default_format)

    def format_date(dt: datetime, default_format: str = '%Y-%m-%d %H:%M:%S') -> str:
        if dt:
            return dt.strftime(format=default_format)
        return ""
