import numpy as np
import matplotlib.pyplot as plt

from src.Blade import Blade
from src.BladeElementTheory import BladeElementTheory
from src.OperationalCondition import OperationalCondition

class PerformanceAnalyzer:
    def __init__(self, blade: Blade, min_wind_speed: float = 0.0, max_wind_speed: float = 25.0, num_points: int = 100, num_blades: int = 3, rho: float = 1.225):
        """
        Initialize PerformanceAnalyzer with a blade object.

        Parameters:
        - blade (Blade): Blade object containing geometry and operational conditions
        - min_wind_speed (float): Minimum wind speed for analysis.
        - max_wind_speed (float): Maximum wind speed for analysis.
        - num_points (int): Number of wind speed points to analyze.
        """
        self.blade = blade
        self.num_blades = num_blades
        self.rho = rho  # Air density in kg/m^3 (standard value at sea level)
        self.min_wind_speed = min_wind_speed
        self.max_wind_speed = max_wind_speed
        self.num_points = num_points
        self.wind_speeds = np.linspace(min_wind_speed, max_wind_speed, num_points)
        self._performance_metrics = None  # Initialize as None, calculate on demand
        self._performance_calculated = False

    def _ensure_performance_calculated(self):
        """Internal method to ensure performance metrics are calculated."""
        if not self._performance_calculated:
            self.calculate_performance()

    def calculate_performance(self):
        """
        Calculate performance metrics for the blade at different wind speeds and store them.

        Returns:
        - A dictionary containing performance metrics (e.g., power, thrust, etc.)
        """
        # Initialize or clear previous results
        self._performance_metrics = {
            "wind_speed": [],
            "power": [],
            "thrust": [],
            "torque": [],
            "ct": [],
            "cp": []
        }

        for wind_speed in self.wind_speeds:
            operational_condition = OperationalCondition(wind_speed=wind_speed, rho=self.rho, num_blades=self.num_blades)
            operational_condition.calculate_angular_velocity(blade=self.blade)
            BET = BladeElementTheory(blade=self.blade)

            # Calculate performance metrics using BladeElementTheory
            thrust , torque, power, ct, cp= BET.compute_aerodynamic_performance(operational_condition=operational_condition)

            # Append results directly to the instance variable
            self._performance_metrics["wind_speed"].append(wind_speed)
            self._performance_metrics["power"].append(power)
            self._performance_metrics["thrust"].append(thrust)
            self._performance_metrics["torque"].append(torque)
            self._performance_metrics["ct"].append(ct)
            self._performance_metrics["cp"].append(cp)


        self._performance_calculated = True # Mark as calculated
        return self._performance_metrics

    @property
    def performance_metrics(self):
        """
        Getter for performance metrics. Calculates them if not already done.
        """
        self._ensure_performance_calculated()
        return self._performance_metrics

    def plot_power_curve(self):
        """
        Plot the power curve of the wind turbine.
        """
        self._ensure_performance_calculated() # Ensure data is calculated

        plt.figure(figsize=(10, 6))
        plt.plot(self._performance_metrics["wind_speed"], self._performance_metrics["power"], label="Power Curve")
        plt.xlabel("Wind Speed (m/s)")
        plt.ylabel("Power (W)")
        plt.title("Wind Turbine Power Curve")
        plt.grid()
        plt.legend()
        # plt.show()

    def plot_thrust_curve(self):
        """
        Plot the thrust curve of the wind turbine.
        """
        self._ensure_performance_calculated() # Ensure data is calculated

        plt.figure(figsize=(10, 6))
        plt.plot(self._performance_metrics["wind_speed"], self._performance_metrics["thrust"], label="Thrust Curve", color='orange')
        plt.xlabel("Wind Speed (m/s)")
        plt.ylabel("Thrust (N)")
        plt.title("Wind Turbine Thrust Curve")
        plt.grid()
        plt.legend()
        # plt.show()
    
    def plot_torque_curve(self):
        """
        Plot the torque curve of the wind turbine.
        """
        self._ensure_performance_calculated() # Ensure data is calculated

        plt.figure(figsize=(10, 6))
        plt.plot(self._performance_metrics["wind_speed"], self._performance_metrics["torque"], label="Torque Curve", color='green')
        plt.xlabel("Wind Speed (m/s)")
        plt.ylabel("Torque (Nm)")
        plt.title("Wind Turbine Torque Curve")
        plt.grid()
        plt.legend()
        # plt.show()