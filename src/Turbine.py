import numpy as np
from typing import List
from .Blade import Blade
from .OperationalCharacteristics import OperationalCondition
from .MomentumTheory import MomentumTheory

class Turbine:
    def __init__(self, blade: Blade, rho: float = 1.225):
        """
        Initialize the Turbine class.
        
        Parameters:
        - blade (Blade): Blade object containing geometry and elements
        - rho (float): Air density [kg/m³], defaults to 1.225
        """
        self.blade = blade
        self.rho = rho
        self.R = max(element.r for element in blade.elements)  # Rotor radius
        self.A = np.pi * self.R**2  # Rotor area

    def compute_performance(self, op_condition: OperationalCondition) -> dict:
        """
        Compute turbine performance metrics for given operational conditions.
        
        Parameters:
        - op_condition (OperationalCondition): Operational condition with wind speed, rpm, and pitch
        
        Returns:
        - dict: Dictionary containing performance metrics (thrust, torque, power, CT, CP)
        """
        wind_speed = op_condition.wind_speed
        rpm = op_condition.rpm
        pitch = np.radians(op_condition.pitch)  # Convert to radians
        omega = rpm * 2 * np.pi / 60  # Convert RPM to rad/s

        # Initialize total thrust and torque
        total_thrust = 0.0
        total_torque = 0.0

        for element in self.blade.elements:
            # Initial guesses for a and a'
            a_guess = 0.3
            a_prime_guess = 0.01
            
            # Calculate flow angle phi
            r = element.r
            phi = np.arctan((1 - a_guess) * wind_speed / ((1 + a_prime_guess) * omega * r))
            
            # Calculate angle of attack (alpha)
            twist_rad = np.radians(element.twist)
            alpha = phi - (pitch + twist_rad)
            
            if element.airfoil and element.airfoil.aero_data:
                # Get lift and drag coefficients
                aero_data = element.airfoil.aero_data
                alphas = np.array([data.alpha for data in aero_data])
                idx = np.argmin(np.abs(alphas - np.degrees(alpha)))
                Cl = aero_data[idx].cl
                Cd = aero_data[idx].cd
                
                # Calculate normal and tangential coefficients
                Cn = Cl * np.cos(phi) + Cd * np.sin(phi)
                Ct = Cl * np.sin(phi) - Cd * np.cos(phi)
                
                # Compute induction factors
                mt = MomentumTheory(a_guess, a_prime_guess, phi, element.solidity, Cn, Ct)
                a, a_prime = mt.compute_induction_factors()
                
                # Calculate local thrust and torque contributions
                dr = element.r * 0.1  # Approximate element length (10% of radius)
                dT = 4 * np.pi * r * self.rho * wind_speed**2 * a * (1 - a) * dr
                dM = 4 * np.pi * r**3 * self.rho * wind_speed * omega * a_prime * (1 - a) * dr
                
                total_thrust += dT
                total_torque += dM

        # Calculate power
        power = total_torque * omega

        # Calculate coefficients
        CT = total_thrust / (0.5 * self.rho * self.A * wind_speed**2)
        CP = power / (0.5 * self.rho * self.A * wind_speed**3)

        return {
            'thrust': total_thrust,
            'torque': total_torque,
            'power': power,
            'CT': CT,
            'CP': CP
        }

    def compute_power_curve(self, operational_conditions: List[OperationalCondition]) -> List[dict]:
        """
        Compute power and thrust curves for a range of operational conditions.
        
        Parameters:
        - operational_conditions (List[OperationalCondition]): List of operational conditions
        
        Returns:
        - List[dict]: List of performance metrics for each operational condition
        """
        performance_data = []
        for condition in operational_conditions:
            metrics = self.compute_performance(condition)
            metrics['wind_speed'] = condition.wind_speed
            performance_data.append(metrics)
        
        return performance_data