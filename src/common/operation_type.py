from enum import Enum


class OperationType(int, Enum):
    SYSTEM_CONF_SETTING = 0
    SYSTEM_CONF_SHIP_INFO = 1

    GENERAL_PREFERENCE = 2
    GENERAL_LIMITATION_WARNING = 3
    GENERAL_LIMITATION_MAX = 4
    GENERAL_UTC_DATE_TIME = 5

    PROPELLER_SETTING = 6

    IO_CONF = 7
    IO_CONF_FACTOR = 8

    USER_ADD = 14
    USER_DELETE = 15
    USER_UPDATE = 16

    ZERO_CAL = 17
    ZERO_CAL_SPS1 = 18
    ZERO_CAL_SPS2 = 19
    PERMISSION_CONF = 20
    TEST_MODE_CONF = 21

    SYSTEM_EXIT = 22

    OFFLINE_DEFAULT_VALUE = 23

    CONNECT_TO_MASTER = 24
    DISCONNECT_FROM_HMI_SERVER = 25

    START_HMI_SERVER = 26
    STOP_HMI_SERVER = 27

    CONNECT_TO_SPS1 = 28
    DISCONNECT_FROM_SPS1 = 29

    CONNECT_TO_SPS2 = 30
    DISCONNECT_FROM_SPS2 = 31

    CONNECT_TO_PLC = 32
    DISCONNECT_FROM_PLC = 33

    CONNECT_TO_GPS = 34
    DISCONNECT_FROM_GPS = 35
    
    @classmethod
    def get_operation_type_name(cls, operation_type: int) -> str:
        return cls(operation_type).name

    @classmethod
    def list_all(cls) -> list:
        return [f"{member.value}: {member.name}" for member in cls]
