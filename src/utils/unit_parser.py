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
    def parse_power(power: float, system_unit: int) -> tuple[int, str]:
        _power = power if power else 0
        if system_unit == 0:
            if _power < 1000:
                return [round(_power), 'W']
            else:
                return [round(_power/1000), 'kW']
        else:
            return [round(UnitConverter.w_to_shp(_power)), 'sHp']

    @staticmethod
    def parse_speed(speed: float) -> tuple[int, str]:
        _speed = float(speed) if speed else 0.0
        return [round(_speed, 1), 'rpm']

    @staticmethod
    def parse_torque(torque: int = 0, system_unit: int = 0) -> tuple[int, str]:
        if system_unit == 0:
            if torque < 1000:
                return [round(torque), 'Nm']
            else:
                return [round(torque/1000), 'kNm']
        else:
            return [round(UnitConverter.nm_to_tm(torque)), 'Tm']

    @staticmethod
    def parse_thrust(thrust: int = 0, system_unit: int = 0) -> tuple[int, str]:
        if system_unit == 0:
            if thrust < 1000:
                return [round(thrust), 'N']
            else:
                return [round(thrust/1000), 'kN']
        else:
            return [round(UnitConverter.n_to_t(thrust)), 'T']
