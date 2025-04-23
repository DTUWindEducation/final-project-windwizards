import numpy as np

from typing import List
from pathlib import Path

from src.Blade import Blade

class OperationalCondition:
    def __init__(self, wind_speed: float, rho: float = 1.225, num_blades: int = 3):
        """
        Initialize the operational condition with wind speed, angular velocity, and air density.
        Wind speed can be a single float.
        
        Parameters:
        - wind_speed (float): Wind speed in m/s.
        - rho (float): Air density in kg/m^3. Default is 1.225 kg/m^3.
        - num_blades (int): Number of blades. Default is 3.
        - rmp (float): Rotations per minute. Default is None.
        - omega (float): Angular velocity in rad/s. Default is None.
        """
        self.wind_speed = wind_speed
        self.rho = rho
        self.num_blades = num_blades
        self.rmp = None  # Placeholder for RPM, to be set by given blade
        self.omega = None # Placeholder for angular velocity, to be set by given blade

        
    def calculate_angular_velocity(self, blade: Blade):
        """
        Calculate the angular velocity in rad/s from RPM.
        
        Parameters:
        - blade (Blade): Blade object containing operational characteristics.
        
        Returns:
        - self: The OperationalCondition object with updated rpm and omega.
        """
        # Interpolate pitch angle based on wind speed
        wind_speeds = np.array([blade.operational_characteristics.characteristics[i].wind_speed for i in range(len(blade.operational_characteristics.characteristics))])
        rpms = np.array([blade.operational_characteristics.characteristics[i].rpm for i in range(len(blade.operational_characteristics.characteristics))])
        
        self.rpm = np.interp(self.wind_speed, wind_speeds, rpms)
        self.omega = self.rpm * 2 * np.pi / 60
        return self

        

    def __repr__(self):
        return (f"OperationalCondition(wind_speed={self.wind_speed},\n"
                f"rho={self.rho}, num_blades={self.num_blades})")
    
    def __str__(self):
        output = (f"Operational Condition:\n"
                f"  Wind Speed: {self.wind_speed} m/s\n"
                f"  Air Density: {self.rho} kg/m^3\n"
                f"  Number of Blades: {self.num_blades}\n")
        if self.rpm is not None:
            output += f"  RPM: {self.rpm}\n"
        if self.omega is not None:
            output += f"  Angular Velocity: {self.omega} rad/s\n"
        return output
