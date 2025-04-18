""" Momentum-Theory
Compute axial (a) and tangential (a') induction factors using actuator disk theory.
"""

import numpy as np
from src.Blade import Blade

class MomentumTheory:
    def __init__(self, blade: Blade, a_guess=0.0, a_prime_guess=0.0, max_iterations=100, tolerance=1e-5):
        """
        Initialize the MomentumTheory class with parameters.

        Parameters:
        - blade (Blade): Blade object containing geometry and operational conditions
        - a_guess (float): Initial guess for axial induction factor
        - a_prime_guess (float): Initial guess for tangential induction factor
        - max_iterations (int): Maximum number of iterations for convergence
        - tolerance (float): Convergence tolerance
        """
        self.blade = blade
        self.a = a_guess
        self.a_prime = a_prime_guess
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
        # Calculate phi for each blade element
        self.wind_speed = blade.wind_speed
        self.omega = blade.omega
        self.elements = blade.elements

        # Execution of induction factor computation
        self.compute_induction_factors()

    def compute_element_induction_factors(self, element, phi, Cn, Ct):
        """
        Compute induction factors for a single blade element.

        Parameters:
        - element (BladeElement): Blade element
        - phi (float): Flow angle [rad]
        - Cn (float): Normal force coefficient
        - Ct (float): Tangential force coefficient

        Returns:
        - tuple: (axial induction factor, tangential induction factor)
        """
        a = self.a
        a_prime = self.a_prime
        solidity = element.solidity

        for _ in range(self.max_iterations):
            # Update axial induction factor
            a_new = 1 / (1 + (4 * np.sin(phi)**2) / (solidity * Cn))
            
            # Update tangential induction factor
            a_prime_new = 1 / (1 + (4 * np.sin(phi) * np.cos(phi)) / (solidity * Ct))
            
            # Check for convergence
            if abs(a - a_new) < self.tolerance and abs(a_prime - a_prime_new) < self.tolerance:
                break
            
            a, a_prime = a_new, a_prime_new

        return a, a_prime

    def compute_induction_factors(self):
        """
        Compute induction factors for all blade elements.

        Returns:
        - list: List of tuples containing (a, a_prime) for each blade element
        """
        
        for element in self.elements:
            # Calculate initial flow angle
            r = element.r
            phi = np.arctan2((1 - self.a) * self.wind_speed, 
                           (1 + self.a_prime) * self.omega * r)
            
            # Get lift and drag coefficients from airfoil data
            if element.airfoil and element.airfoil.aero_data:
                # Calculate angle of attack
                twist_rad = np.radians(element.twist)
                pitch_rad = np.radians(self.blade.operational_conditions.pitch)
                alpha = phi - (pitch_rad + twist_rad)
                
                # Find closest alpha in aero data
                aero_data = element.airfoil.aero_data
                alphas = np.array([data.alpha for data in aero_data])
                idx = np.argmin(np.abs(alphas - np.degrees(alpha)))
                Cl = aero_data[idx].cl
                Cd = aero_data[idx].cd
                
                # Calculate normal and tangential coefficients
                Cn = Cl * np.cos(phi) + Cd * np.sin(phi)
                Ct = Cl * np.sin(phi) - Cd * np.cos(phi)
                
                # Compute induction factors for this element
                a, a_prime = self.compute_element_induction_factors(element, phi, Cn, Ct)

                phi = np.arctan2((1 - self.a) * self.wind_speed, 
                           (1 + self.a_prime) * self.omega * r)

            element.alpha = alpha
            element.cl = Cl
            element.cd = Cd
            element.a = a
            element.a_prime = a_prime
            element.phi = phi
            element.Cn = Cn
            element.Ct = Ct

        return 


