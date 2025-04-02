import flet as ft

from utils.unit_converter import UnitConverter


class UnitParser:
    @staticmethod
    def parse_energy(energy: float, system_unit: int) -> tuple[float, str]:
        _energy = energy if energy is not None else 0
        if system_unit == 0:
            if _energy < 1000:
                return [float(f'{_energy:.1f}'), 'kWh']
            else:
                return [float(f'{_energy/1000:.1f}'), 'MWh']
        else:
            return [float(f'{_energy/1000:.1f}'), 'kWh']

    @staticmethod
    def parse_power(power: float, system_unit: int) -> tuple[float, str]:
        # if power is less than 1000, return power and the unit is W else return power and the unit is kW
        _power = power if power is not None else 0
        if system_unit == 0:
            if _power < 1000:
                return [float(f'{_power:.1f}'), 'W']
            else:
                return [float(f'{_power/1000:.1f}'), 'kW']
        else:
            return [float(f'{UnitConverter.w_to_hp(_power):.1f}'), 'hp']

    @staticmethod
    def parse_speed(speed: float) -> tuple[float, str]:
        _speed = speed if speed is not None else 0
        return [float(f'{_speed:.1f}'), 'rpm']

    @staticmethod
    def parse_torque(torque: float, system_unit: int) -> tuple[float, str]:
        # if torque is less than 1000, return torque and the unit is Nm else return torque and the unit is Nm/s
        _torque = torque if torque is not None else 0
        if system_unit == 0:
            if _torque < 1000:
                return [float(f'{_torque:.1f}'), 'Nm']
            else:
                return [float(f'{_torque/1000:.1f}'), 'kN·m']
        else:
            _metric_torque = UnitConverter.nm_to_gfm(_torque)
            if _metric_torque < 1000:
                return [float(f'{_metric_torque:.1f}'), 'gf·m']
            else:
                return [float(f'{_metric_torque/1000:.1f}'), 'kgf·m']

    @staticmethod
    def parse_thrust(thrust: float, system_unit: int) -> tuple[float, str]:
        # if thrust is less than 1000, return thrust and the unit is N else return thrust and the unit is kN
        _thrust = thrust if thrust is not None else 0
        if system_unit == 0:
            if _thrust < 1000:
                return [float(f'{_thrust:.1f}'), 'N']
            else:
                return [float(f'{_thrust/1000:.1f}'), 'kN']
        else:
            _metric_thrust = UnitConverter.n_to_gf(_thrust)
            if _metric_thrust < 1000:
                return [float(f'{_metric_thrust:.1f}'), 'gf']
            else:
                return [float(f'{_metric_thrust/1000:.1f}'), 'kgf']
