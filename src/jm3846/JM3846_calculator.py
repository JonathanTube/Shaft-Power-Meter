

import logging
import math
from common.global_data import gdata

const_central = 32768.0  # 16位ADC中间值


class JM3846Calculator:
    """物理量计算类 (单一职责: 力学计算)"""

    def calculate_mv_per_v(self, ad_value: int, gain: int) -> float:
        # logging.info(f"calculate_mv_per_v: const_central={const_central}, ad_value={ad_value}, gain={gain}")
        """计算中间值, mv/v"""
        """这里就是：const_central - ad_value，不然正负颠倒"""
        numerator = (const_central - ad_value) * (10 ** 3)
        denominator = const_central * gain
        if denominator == 0:
            return 0
        result = numerator / denominator
        # logging.info(f"calculate_mv_per_v: result={result}\r\n")
        return result

    def calculate_microstrain(self, mv_per_v: float) -> float:
        """AD值转微应变 (精确浮点计算)"""
        # logging.info(f"calculate_microstrain: const_central={const_central}, ad_value={ad_value}, gain={gain}")
        if gdata.sensitivity_factor_k == 0:
            return 0
        result = mv_per_v / gdata.sensitivity_factor_k * (10**3)
        logging.info(f"calculate_microstrain: result={result}")
        return result

    def calculate_torque(self, microstrain: float) -> float:
        """计算扭矩 (N·m)"""
        D = gdata.bearing_outer_diameter_D
        d = gdata.bearing_inner_diameter_d

        numerator = math.pi * microstrain * gdata.elastic_modulus_E * (D**4 - d**4)
        denominator = (1 + gdata.poisson_ratio_mu) * 16 * D
        if denominator == 0:
            return 0
        result = numerator / denominator
        return abs(result)

    def calculate_thrust(self, mv_per_v: float) -> float:
        """计算推力 (N)"""
        diameter_diff = (gdata.bearing_outer_diameter_D / 2) ** 2 - (gdata.bearing_inner_diameter_d / 2) ** 2
        numerator = 2 * mv_per_v * math.pi * gdata.elastic_modulus_E * diameter_diff
        denominator = gdata.sensitivity_factor_k * (1 + gdata.poisson_ratio_mu)
        if denominator == 0:
            return 0
        result = (numerator / denominator) * 10 ** 3
        return abs(result)
