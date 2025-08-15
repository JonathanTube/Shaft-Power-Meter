

import logging
import math
from common.global_data import gdata

const_central = 32768.0  # 16位ADC中间值


class JM3846Calculator:
    """物理量计算类 (单一职责: 力学计算)"""
    @staticmethod
    def calculate_mv_per_v(ad_value: int, gain: int) -> float:
        # logging.info(f"calculate_mv_per_v: const_central={const_central}, ad_value={ad_value}, gain={gain}")
        """计算中间值, mv/v"""
        """这里就是：const_central - ad_value，不然正负颠倒"""
        if gain is None:
            return 0

        numerator = (const_central - ad_value) * (10 ** 3)
        denominator = const_central * gain
        if denominator == 0:
            return 0
        result = numerator / denominator
        # logging.info(f"calculate_mv_per_v: result={result}\r\n")
        return result

    @staticmethod
    def calculate_microstrain(mv_per_v: float) -> float:
        """AD值转微应变 (精确浮点计算)"""
        # logging.info(f"calculate_microstrain: const_central={const_central}, ad_value={ad_value}, gain={gain}")
        if gdata.configFactor.sensitivity_factor_k == 0:
            return 0
        result = mv_per_v / gdata.configFactor.sensitivity_factor_k * (10**3)
        # logging.info(f"calculate_microstrain: result={result}")
        return result

    @staticmethod
    def calculate_torque(microstrain: float) -> float:
        """计算扭矩 (N·m)"""
        D = gdata.configFactor.bearing_outer_diameter_D
        d = gdata.configFactor.bearing_inner_diameter_d

        numerator = math.pi * microstrain * \
            gdata.configFactor.elastic_modulus_E * (D**4 - d**4)
        denominator = (1 + gdata.configFactor.poisson_ratio_mu) * 16 * D
        if denominator == 0:
            return 0
        result = numerator / denominator
        return abs(result)

    @staticmethod
    def calculate_thrust(mv_per_v: float) -> float:
        """计算推力 (N)"""
        diameter_diff = (gdata.configFactor.bearing_outer_diameter_D / 2) ** 2 - \
            (gdata.configFactor.bearing_inner_diameter_d / 2) ** 2

        numerator = 2 * mv_per_v * math.pi * gdata.configFactor.elastic_modulus_E * diameter_diff

        denominator = gdata.configFactor.sensitivity_factor_k * (1 + gdata.configFactor.poisson_ratio_mu)

        if denominator == 0:
            return 0

        result = (numerator / denominator) * 10 ** 3
        return abs(result)
