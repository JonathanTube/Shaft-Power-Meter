import math


class UnitConverter:
    # https://www.unitconverters.net/power/watts-to-hp.htm
    @staticmethod
    def w_to_shp(value):
        # 1 W = 0.0013596216 sHp
        return round(value * 0.0013596216, 2)

    @staticmethod
    def shp_to_w(value):
        # 1 sHp = 735.4987593 W
        return math.ceil(value * 735.4987593)

    @staticmethod
    def nm_to_tm(value):
        # 1 Nm = 0.0001019716213 Tm
        return value * 0.0001019716213

    @staticmethod
    def n_to_t(value):
        # 1 N = 0.0001019716213 T
        return value * 0.0001019716213

    @staticmethod
    def kwh_to_shph(value):
        # 1 kWh =  1.3410220896 sHp·h
        return value * 1.3410220896
