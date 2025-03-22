import flet as ft


class UnitParser:
    @staticmethod
    def parse_power(power: float) -> list[str]:
        # if power is less than 1000, return power and the unit is W else return power and the unit is kW
        _power = power if power is not None else 0
        if _power < 1000:
            return [f'{_power:.2f}', 'W']
        else:
            return [f'{_power/1000:.2f}', 'kW']

    @staticmethod
    def parse_speed(speed: float) -> list[str]:
        _speed = speed if speed is not None else 0
        return [f'{_speed:.2f}', 'rps']

    @staticmethod
    def parse_torque(torque: float) -> list[str]:
        # if torque is less than 1000, return torque and the unit is Nm else return torque and the unit is Nm/s
        _torque = torque if torque is not None else 0
        if _torque < 1000:
            return [f'{_torque:.2f}', 'Nm']
        else:
            return [f'{_torque/1000:.2f}', 'kNm']

    @staticmethod
    def parse_thrust(thrust: float) -> list[str]:
        # if thrust is less than 1000, return thrust and the unit is N else return thrust and the unit is kN
        _thrust = thrust if thrust is not None else 0
        if _thrust < 1000:
            return [f'{_thrust:.2f}', 'N']
        else:
            return [f'{_thrust/1000:.2f}', 'kN']
