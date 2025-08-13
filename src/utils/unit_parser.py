import flet as ft

from utils.unit_converter import UnitConverter


class UnitParser:
    @staticmethod
    def parse_energy(energy: float, system_unit: int) -> tuple[int, str]:
        _energy = energy if energy is not None else 0
        if system_unit == 0:
            return [round(_energy), 'kWh']
        else:
            return [round(UnitConverter.kwh_to_shph(_energy)), 'SHph']

    @staticmethod
    def parse_power(power: float, system_unit: int, shrink: bool = False) -> tuple[int, str]:
        _power = power if power is not None else 0
        if system_unit == 0:
            if shrink and _power < 1000:
                return [round(_power), 'W']
            else:
                return [round(_power/1000), 'kW']
        else:
            return [round(UnitConverter.w_to_shp(_power)), 'sHp']

    @staticmethod
    def parse_speed(speed: float) -> tuple[int, str]:
        _speed = speed if speed is not None else 0
        return [round(_speed), 'rpm']

    @staticmethod
    def parse_torque(torque: float, system_unit: int, shrink: bool = False) -> tuple[int, str]:
        _torque = torque if torque is not None else 0
        if system_unit == 0:
            if shrink and _torque < 1000:
                return [round(_torque), 'Nm']
            else:
                return [round(_torque/1000), 'kNm']
        else:
            return [round(UnitConverter.nm_to_tm(_torque)), 'Tm']

    @staticmethod
    def parse_thrust(thrust: float, system_unit: int, shrink: bool = False) -> tuple[int, str]:
        _thrust = thrust if thrust is not None else 0
        if system_unit == 0:
            if shrink and _thrust < 1000:
                return [round(_thrust), 'N']
            else:
                return [round(_thrust/1000), 'kN']
        else:
            return [round(UnitConverter.n_to_t(_thrust)), 'T']
