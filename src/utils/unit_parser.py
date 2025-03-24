import flet as ft


class UnitParser:
    @staticmethod
    def parse_power(power: float) -> tuple[float, str]:
        # if power is less than 1000, return power and the unit is W else return power and the unit is kW
        _power = power if power is not None else 0
        if _power < 1000:
            return [float(f'{_power:.2f}'), 'W']
        else:
            return [float(f'{_power/1000:.2f}'), 'kW']

    @staticmethod
    def parse_speed(speed: float) -> tuple[float, str]:
        _speed = speed if speed is not None else 0
        return [float(f'{_speed:.2f}'), 'rps']

    @staticmethod
    def parse_torque(torque: float) -> tuple[float, str]:
        # if torque is less than 1000, return torque and the unit is Nm else return torque and the unit is Nm/s
        _torque = torque if torque is not None else 0
        if _torque < 1000:
            return [float(f'{_torque:.2f}'), 'Nm']
        else:
            return [float(f'{_torque/1000:.2f}'), 'kNm']

    @staticmethod
    def parse_thrust(thrust: float) -> tuple[float, str]:
        # if thrust is less than 1000, return thrust and the unit is N else return thrust and the unit is kN
        _thrust = thrust if thrust is not None else 0
        if _thrust < 1000:
            return [float(f'{_thrust:.2f}'), 'N']
        else:
            return [float(f'{_thrust/1000:.2f}'), 'kN']
