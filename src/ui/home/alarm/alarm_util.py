import logging
from common.const_alarm_type import AlarmType


class AlarmUtil:
    def get_event_name(page, alarm_type: str) -> str:
        try:
            if page is None or page.session is None:
                return ''

            session = page.session
            match alarm_type:
                case AlarmType.MASTER_PLC:
                    return session.get("lang.alarm.master_plc_disconnected")

                case AlarmType.MASTER_GPS:
                    return session.get("lang.alarm.master_gps_disconnected")

                case AlarmType.MASTER_SPS:
                    return session.get("lang.alarm.master_sps_disconnected")

                case AlarmType.MASTER_SPS2:
                    return session.get("lang.alarm.master_sps2_disconnected")

                case AlarmType.MASTER_SERVER:
                    return session.get("lang.alarm.master_server_stopped")

                case AlarmType.SLAVE_MASTER:
                    return session.get("lang.alarm.slave_master_disconnected")

                case AlarmType.POWER_OVERLOAD:
                    return session.get("lang.alarm.power_overload")

                case _:
                    return session.get("lang.alarm.unknown")
        except:
            logging.exception("exception occured at AlarmUtil.get_event_name")

        return ''
