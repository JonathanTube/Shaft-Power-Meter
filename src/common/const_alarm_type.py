from enum import Enum


class AlarmType(int, Enum):
    MASTER_PLC_DISCONNECTED = 0
    MASTER_PLC_CONNECTED = 1

    MASTER_GPS_DISCONNECTED = 2
    MASTER_GPS_CONNECTED = 3

    SLAVE_GPS_DISCONNECTED = 4
    SLAVE_GPS_CONNECTED = 5

    MASTER_SPS_DISCONNECTED = 6
    MASTER_SPS_CONNECTED = 7

    MASTER_SPS2_DISCONNECTED = 8
    MASTER_SPS2_CONNECTED = 9

    MASTER_SERVER_STOPPED = 10
    MASTER_SERVER_STARTED = 11

    SLAVE_CLIENT_DISCONNECTED = 12
    SLAVE_CLIENT_CONNECTED = 13

    POWER_OVERLOAD = 98
    POWER_OPTIMAL_LOAD =  99

    APP_UNEXPECTED_EXIT = 100


    @classmethod
    def get_alarm_type_name(cls, alarm_type: int) -> str:
        return cls(alarm_type).name

    @classmethod
    def list_all(cls) -> list:
        return [f"{member.value}: {member.name}" for member in cls]
