class UnitConverter:
    @staticmethod
    def w_to_hp(value):
        # 1 W = 0.0013596216 hp
        return value * 0.0013596216

    @staticmethod
    def nm_to_kgfm(value):
        # 1 Nm = 101.9716213 kgfm
        return value * 101.9716213

    @staticmethod
    def n_to_kgf(value):
        # 1 N = 0.1019716213 kgf
        return value * 0.1019716213

    @staticmethod
    def kwh_to_shph(value):
        # 1 kWh = 1.3404825737 SHph
        return value * 1.3404825737