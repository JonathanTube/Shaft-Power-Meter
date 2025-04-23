from enum import Enum


class AlarmType(int, Enum):
    """报警类型枚举"""
    PLC_DISCONNECTED = 0
    GPS_DISCONNECTED = 1
    SPS_DISCONNECTED = 2
    APP_UNEXPECTED_EXIT = 3
    POWER_OVERLOAD = 4

    @classmethod
    def get_alarm_type_name(cls, alarm_type: int) -> str:
        """通过数值获取报警类型名称（兼容旧代码用法）"""
        return cls(alarm_type).name  # 直接返回枚举成员的name属性

    @classmethod
    def list_all(cls) -> list:
        """获取所有枚举成员的友好展示"""
        return [f"{member.value}: {member.name}" for member in cls]
