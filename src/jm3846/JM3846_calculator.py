

import logging
import math

from db.models.factor_conf import FactorConf

const_central = 32768.0  # 16位ADC中间值


class JM3846Calculator:
    """物理量计算类 (单一职责: 力学计算)"""

    def __init__(self):
        self.config: FactorConf = None

    def calculate_mv_per_v(self, ad_value: int, gain: int) -> float:
        if self.config is None:
            self.config = FactorConf.get()

        # logging.info(f"calculate_mv_per_v: const_central={const_central}, ad_value={ad_value}, gain={gain}")
        """计算中间值, mv/v"""
        numerator = (ad_value - const_central) * (10 ** 3)
        denominator = const_central * gain
        if denominator == 0:
            return 0
        result = numerator / denominator
        # logging.info(f"calculate_mv_per_v: result={result}\r\n")
        return result

    def calculate_microstrain(self, ad_value: int, gain: int) -> float:
        """AD值转微应变 (精确浮点计算)"""
        # logging.info(f"calculate_microstrain: const_central={const_central}, ad_value={ad_value}, gain={gain}")
        mv_v = self.calculate_mv_per_v(ad_value, gain)
        if self.config.sensitivity_factor_k == 0:
            return 0
        result = mv_v / self.config.sensitivity_factor_k * (10**3)
        logging.info(f"calculate_microstrain: result={result}")
        return result

    def calculate_torque(self, ad_value: int, gain: int) -> float:
        """计算扭矩 (N·m)"""
        microstrain = self.calculate_microstrain(ad_value, gain)
        D = self.config.bearing_outer_diameter_D
        d = self.config.bearing_inner_diameter_d

        numerator = math.pi * microstrain * self.config.elastic_modulus_E * (D**4 - d**4)
        denominator = (1 + self.config.poisson_ratio_mu) * 16 * D
        if denominator == 0:
            return 0
        return numerator / denominator

    def calculate_thrust(self, ad_value: int, gain: int) -> float:
        """计算推力 (N)"""
        mv_v = self.calculate_mv_per_v(ad_value, gain)
        diameter_diff = (self.config.bearing_outer_diameter_D / 2) ** 2 - (self.config.bearing_inner_diameter_d / 2) ** 2
        numerator = 2 * mv_v * math.pi * self.config.elastic_modulus_E * diameter_diff
        denominator = self.config.sensitivity_factor_k * (1 + self.config.poisson_ratio_mu)
        if denominator == 0:
            return 0
        return (numerator / denominator) * 10 ** 3
