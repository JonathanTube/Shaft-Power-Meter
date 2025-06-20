from enum import Enum


class AlarmType(int, Enum):
    PLC_DISCONNECTED = 0
    GPS_DISCONNECTED = 1

    SPS1_DISCONNECTED = 2
    SPS2_DISCONNECTED = 3

    MASTER_SERVER_STOPPED = 4
    SLAVE_DISCONNECTED = 5

    APP_UNEXPECTED_EXIT = 6
    POWER_OVERLOAD = 7


    @classmethod
    def get_alarm_type_name(cls, alarm_type: int) -> str:
        return cls(alarm_type).name

    @classmethod
    def list_all(cls) -> list:
        return [f"{member.value}: {member.name}" for member in cls]
