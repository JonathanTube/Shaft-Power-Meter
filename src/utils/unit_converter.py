import math


class UnitConverter:
    @staticmethod
    def kw_to_w(value: float):
        # 1 kW = 1000 W
        return round(value * 1000, 1)

    @staticmethod
    def knm_to_nm(value: float):
        # 1 kNm = 1000 Nm
        return round(value * 1000, 1)

    # https://www.unitconverters.net/power/watts-to-hp.htm
    @staticmethod
    def w_to_shp(value: float):
        # 1 W = 0.0013596216 sHp
        return round(value * 0.0013596216, 1)

    @staticmethod
    def shp_to_w(value: float):
        # 1 sHp = 735.4987593 W
        return round(value * 735.4987593, 1)

    @staticmethod
    def nm_to_tm(value: float):
        # 1 Nm = 0.0001019716213 Tm
        return round(value * 0.0001019716213, 1)

    @staticmethod
    def tm_to_nm(value: float):
        # 1 Tm = 9806.65 Nm
        return round(value * 9806.65, 1)

    @staticmethod
    def n_to_t(value: float):
        # 1 N = 0.0001019716213 T
        return round(value * 0.0001019716213, 1)

    @staticmethod
    def kwh_to_shph(value: float):
        # 1 kWh =  1.3410220896 sHp·h
        return round(value * 1.3410220896, 1)
