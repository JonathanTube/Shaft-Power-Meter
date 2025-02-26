class UnitConverter:
    @staticmethod
    def rpm_to_rpm(value):
        return value

    @staticmethod
    def kw_to_shp(value):
        # 1 kW = 1.34102 SHp
        return value * 1.34102

    @staticmethod
    def shp_to_kw(value):
        # 1 SHp = 0.7457 kW
        return value * 0.7457

    @staticmethod
    def knm_to_tm(value):
        # 1 kNm = 0.101971621 Tm
        return value * 0.101971621

    @staticmethod
    def tm_to_knm(value):
        # 1 Tm = 9.80665 kNm
        return value * 9.80665

    @staticmethod
    def kn_to_t(value):
        # 1 kN = 0.101971621 T
        return value * 0.101971621

    @staticmethod
    def t_to_kn(value):
        # 1 T = 9.80665 kN
        return value * 9.80665

    @staticmethod
    def kwh_to_shph(value):
        # 1 kWh = 1.3404825737 SHph
        return value * 1.3404825737

    @staticmethod
    def shph_to_kwh(value):
        # 1 SHph = 0.7457 kWh
        return value * 0.7457
