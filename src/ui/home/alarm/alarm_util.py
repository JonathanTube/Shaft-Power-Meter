import logging
from common.const_alarm_type import AlarmType


class AlarmUtil:
    def get_event_name(page, alarm_type: str, is_recovery: bool) -> str:
        try:
            if page is None or page.session is None:
                return ''

            session = page.session
            match alarm_type:
                case AlarmType.MASTER_PLC:
                    if is_recovery:
                        return session.get("lang.alarm.master_plc_connected")
                    return session.get("lang.alarm.master_plc_disconnected")

                case AlarmType.SLAVE_GPS:
                    if is_recovery:
                        return session.get("lang.alarm.slave_gps_connected")
                    return session.get("lang.alarm.slave_gps_disconnected")

                case AlarmType.MASTER_GPS:
                    if is_recovery:
                        return session.get("lang.alarm.master_gps_connected")
                    return session.get("lang.alarm.master_gps_disconnected")

                case AlarmType.MASTER_SPS:
                    if is_recovery:
                        return session.get("lang.alarm.master_sps_connected")
                    return session.get("lang.alarm.master_sps_disconnected")

                case AlarmType.MASTER_SPS2:
                    if is_recovery:
                        return session.get("lang.alarm.master_sps2_connected")
                    return session.get("lang.alarm.master_sps2_disconnected")

                case AlarmType.MASTER_SERVER:
                    if is_recovery:
                        return session.get("lang.alarm.master_server_started")
                    return session.get("lang.alarm.master_server_stopped")

                case AlarmType.SLAVE_CLIENT:
                    if is_recovery:
                        return session.get("lang.alarm.slave_master_connected")
                    return session.get("lang.alarm.slave_master_disconnected")

                case AlarmType.POWER_OVERLOAD:
                    if is_recovery:
                        return session.get("lang.alarm.power_optimal_load")
                    return session.get("lang.alarm.power_overload")

                case _:
                    return session.get("lang.alarm.unknown")
        except:
            logging.exception("exception occured at AlarmUtil.get_event_name")

        return ''
