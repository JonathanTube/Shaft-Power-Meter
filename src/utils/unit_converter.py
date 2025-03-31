class UnitConverter:
    # https://www.unitconverters.net/power/watts-to-hp.htm
    @staticmethod
    def w_to_hp(value):
        # 1 W = 0.0013596216 hp
        return value * 0.0013596216

    # https://www.unitconverters.net/torque/newton-meter-to-gram-force-meter.htm
    # gfm = gram-force meter
    @staticmethod
    def nm_to_gfm(value):
        # 1 Nm = 101.9716213 gfm
        return value * 101.9716213

    # https://www.unitconverters.net/force/newton-to-gram-force.htm
    # gf = gram-force
    @staticmethod
    def n_to_gf(value):
        # 1 N = 101.9716213 gf
        return value * 101.9716213

    # https://www.unitconverters.net/energy/kilowatt-hour-to-horsepower-metric-hour.htm
    # hph = horsepower metric hour
    @staticmethod
    def kwh_to_hph(value):
        # 1 kWh = 1.3596216173 hph
        return value * 1.3596216173
