import math


class FormulaCalculator:
    @staticmethod
    def calculate_torque(D, d, E, μ, k):
        """
        Calculate the torque.

        Parameters:
        D (float): Bearing outer diameter (in mm).
        d (float): Bearing inner diameter (in mm).
        E (float): Elastic modulus (in GPa).
        μ (float): Poisson's ratio.
        k (float): Sensitivity factor.

        Returns:
        float: The calculated torque.
        """
        # Calculate 极惯性矩 (polar moment of inertia)
        polar_moment_of_inertia = (D**4 - d**4) * math.pi / 32

        # Calculate 剪切模量 (shear modulus)
        shear_modulus = E / (2000 * (μ + 1))

        # Calculate torque (Nm)
        torque = polar_moment_of_inertia * shear_modulus * k * 0.001 / 5 / D
        return abs(torque)

    @staticmethod
    def calculate_thrust(D, d, E, μ, k):
        """
        Calculate the thrust.

        Parameters:
        D (float): Bearing outer diameter (in mm).
        d (float): Bearing inner diameter (in mm).
        E (float): Elastic modulus (in GPa).
        μ (float): Poisson's ratio.
        k (float): Sensitivity factor.

        Returns:
        float: The calculated thrust.
        """
        R = D/2
        r = d/2
        # Calculate 截面积 (cross-sectional area)
        cross_sectional_area = (R**2 - r**2) * math.pi

        # Calculate thrust (N)
        thrust = (cross_sectional_area / (1 + μ)) * E * k * 0.001 / 5
        return abs(thrust)

    @staticmethod
    def calculate_rpm(t):
        """
        Calculate the RPM.

        Parameters:
        t (float): Period, time taken for one rotation of the rotor (in seconds).

        Returns:
        float: The calculated RPM.
        """
        if t <= 0:
            raise ValueError("Period must be greater than zero.")
        rpm = 60 / t
        return abs(rpm)

    @staticmethod
    def calculate_instant_power(torque, rpm):
        """
        Calculate the instant power.

        Parameters:
        torque (float): Torque (in Nm).
        rpm (float): Shaft speed in revolutions per minute (RPM).

        Returns:
        float: The calculated power (in W).
        """
        power = (2 * math.pi * rpm * torque) / 60
        return abs(round(power, 2))

    @staticmethod
    def calculate_average_power_kw(sum_of_power, hours):
        """
        Calculate the average power in kW.

        Parameters:
        sum_of_power (float): Sum of power values (in W).
        hours (float): Total time period in hours.

        Returns:
        float: The average power (in kW).
        """
        total_seconds = hours * 3600
        average_power_w = sum_of_power / total_seconds  # Average power in W
        average_power_kw = average_power_w / 1000  # Convert W to kW
        return abs(average_power_kw)

    @staticmethod
    def calculate_energy_kwh(sum_of_power):
        """
        Calculate the energy in kWh.

        Parameters:
        sum_of_power (float): Sum of power values (in W).
        hours (float): Total time period in hours.

        Returns:
        float: The energy in kWh.
        """
        total_seconds = 60 * 60
        total_energy_wh = sum_of_power / total_seconds
        energy_kwh = total_energy_wh / 1000  # Convert Wh to kWh
        return abs(energy_kwh)
