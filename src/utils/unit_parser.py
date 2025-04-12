import flet as ft

from utils.unit_converter import UnitConverter


class UnitParser:
    @staticmethod
    def parse_energy(energy: float, system_unit: int) -> tuple[float, str]:
        _energy = energy if energy is not None else 0
        if system_unit == 0:
            return [float(f'{_energy:.2f}'), 'kWh']
        else:
            return [float(f'{UnitConverter.kwh_to_shph(_energy):.2f}'), 'SHph']

    @staticmethod
    def parse_power(power: float, system_unit: int, shrink: bool = True) -> tuple[float, str]:
        _power = power if power is not None else 0
        if system_unit == 0:
            if shrink and _power < 1000:
                return [float(f'{_power:.1f}'), 'W']
            else:
                return [float(f'{_power/1000:.1f}'), 'kW']
        else:
            return [float(f'{UnitConverter.w_to_shp(_power):.1f}'), 'SHp']

    @staticmethod
    def parse_speed(speed: float) -> tuple[float, str]:
        _speed = speed if speed is not None else 0
        return [float(f'{_speed:.1f}'), 'rpm']

    @staticmethod
    def parse_torque(torque: float, system_unit: int, shrink: bool = True) -> tuple[float, str]:
        _torque = torque if torque is not None else 0
        if system_unit == 0:
            if shrink and _torque < 1000:
                return [float(f'{_torque:.1f}'), 'Nm']
            else:
                return [float(f'{_torque/1000:.1f}'), 'kNm']
        else:
            return [float(f'{UnitConverter.nm_to_tm(_torque):.1f}'), 'Tm']

    @staticmethod
    def parse_thrust(thrust: float, system_unit: int, shrink: bool = True) -> tuple[float, str]:
        _thrust = thrust if thrust is not None else 0
        if system_unit == 0:
            if shrink and _thrust < 1000:
                return [float(f'{_thrust:.1f}'), 'N']
            else:
                return [float(f'{_thrust/1000:.1f}'), 'kN']
        else:
            return [float(f'{UnitConverter.n_to_t(_thrust):.1f}'), 'T']
