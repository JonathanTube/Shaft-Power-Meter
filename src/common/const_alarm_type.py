from enum import Enum


class AlarmType(int, Enum):
    MASTER_PLC_DISCONNECTED = 0

    MASTER_GPS_DISCONNECTED = 1
    SLAVE_GPS_DISCONNECTED = 2

    MASTER_SPS1_DISCONNECTED = 3
    MASTER_SPS2_DISCONNECTED = 4

    MASTER_SERVER_STOPPED = 5
    SLAVE_CLIENT_DISCONNECTED = 6

    APP_UNEXPECTED_EXIT = 7
    POWER_OVERLOAD = 8


    @classmethod
    def get_alarm_type_name(cls, alarm_type: int) -> str:
        return cls(alarm_type).name

    @classmethod
    def list_all(cls) -> list:
        return [f"{member.value}: {member.name}" for member in cls]
