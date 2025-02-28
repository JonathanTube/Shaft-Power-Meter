import pytest
from src.utils.formula_cal import FormulaCalculator
import math


def test_calculate_torque():
    D = 100.0  # mm
    d = 50.0   # mm
    E = 210.0  # GPa
    μ = 0.3    # Poisson's ratio
    k = 1.5    # Sensitivity factor

    expected_torque = 2.230172068541432  # Nm

    calculated_torque = FormulaCalculator.calculate_torque(D, d, E, μ, k)

    assert pytest.approx(calculated_torque, 0.0001) == expected_torque


def test_calculate_thrust():
    D = 50.0   # mm
    d = 20.0   # mm
    E = 210.0  # GPa
    μ = 0.3    # Poisson's ratio
    k = 1.5    # Sensitivity factor

    # Fixed expected value calculated using the formula
    expected_thrust = 79.929366936524931817039946078436  # N

    calculated_thrust = FormulaCalculator.calculate_thrust(D, d, E, μ, k)

    assert pytest.approx(calculated_thrust, 0.0001) == expected_thrust


def test_calculate_rpm():
    t = 0.5  # seconds
    expected_rpm = 120.0  # RPM

    calculated_rpm = FormulaCalculator.calculate_rpm(t)

    assert pytest.approx(calculated_rpm, 0.0001) == expected_rpm

    with pytest.raises(ValueError):
        FormulaCalculator.calculate_rpm(0)

    with pytest.raises(ValueError):
        FormulaCalculator.calculate_rpm(-1)


def test_calculate_instant_power():
    torque = 1.0  # Nm
    rpm = 1000.0  # RPM

    expected_power = 104.71975511965977461542144610932  # W
    calculated_power = FormulaCalculator.calculate_instant_power(torque, rpm)

    assert pytest.approx(calculated_power, 0.0001) == expected_power


def test_calculate_average_power_kw():
    sum_of_power = 792000  # Sum of power values in W
    hours = 0.0611  # Total time period in hours (220 seconds / 3600)
    expected_average_power_kw = 3.6  # Expected average power in kW
    result = FormulaCalculator.calculate_average_power_kw(sum_of_power, hours)
    assert pytest.approx(result, 0.01) == expected_average_power_kw


def test_calculate_energy_kwh():
    sum_of_power = 792000  # Sum of power values in W
    expected_energy_kwh = 0.22  # Expected energy in kWh
    result = FormulaCalculator.calculate_energy_kwh(sum_of_power)
    assert pytest.approx(result, 0.01) == expected_energy_kwh


def test_calculate_average_power_kw_and_energy_kwh():
    sum_of_power = 792000  # Sum of power values in W
    hours = 0.0611  # Total time period in hours (220 seconds / 3600)

    kw = FormulaCalculator.calculate_average_power_kw(sum_of_power, hours)
    kwh = FormulaCalculator.calculate_energy_kwh(sum_of_power)
    assert kw * hours == kwh
