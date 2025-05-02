import numpy as np
from src.Blade import Blade
from src.OperationalCondition import OperationalCondition

class BladeElementTheory:
    def __init__(self, blade: Blade):
        """
        Initialize BladeElementTheory with a blade object.
        
        Parameters:
        - blade (Blade): Blade object containing geometry and operational conditions
        """
        self.blade = blade
        
    def calculate_solidity(self, operational_conditions=None, chord=None, r=None, solidity=None):
        """
        Calculates the solidity of the blade element.

        Args:
            operational_conditions: Operational conditions containing the number of blades.

        Returns:
            float: Solidity of the blade element.
        """
        num_blades = operational_conditions.num_blades

        if r == 0:
            solidity = 1
            return solidity

        solidity = (num_blades * chord) / (2 * np.pi * r)
        solidity = min(solidity, 1)  # Solidity cannot exceed 1 for physical reasons
        return solidity

    def compute_element_induction_factors(self, a, a_prime, wind_speed, omega, r, chord, phi, Cn, Ct, tolerance=1e-5, max_iterations=100):
        """
        Computes the induction factors for a single blade element.

        Args:
            a (float): Initial axial induction factor.
            a_prime (float): Initial tangential induction factor.
            wind_speed (float): Wind speed [m/s].
            omega (float): Rotational speed [rad/s].
            r (float): Spanwise position [m].
            phi (float): Flow angle [rad].
            Cn (float): Normal force coefficient.
            Ct (float): Tangential force coefficient.
            tolerance (float): Convergence tolerance.
            max_iterations (int): Maximum number of iterations.

        Returns:
            tuple: Axial and tangential induction factors (a, a_prime).
        """
        for _ in range(max_iterations):
            phi = np.arctan2((1 - a) * wind_speed, (1 + a_prime) * omega * r)

            solidity = self.calculate_solidity(operational_conditions=None, chord=chord, r=r, solidity=None)

            a_new = 1 / ((4 * np.sin(phi) ** 2) / (self.solidity * Cn) + 1)
            a_prime_new = 1 / ((4 * np.sin(phi) * np.cos(phi)) / (solidity * Ct) - 1)

            if abs(a - a_new) < tolerance and abs(a_prime - a_prime_new) < tolerance:
                break

            a, a_prime = a_new, a_prime_new

        return a, a_prime

    def compute_induction_factors(self, radius=0.0, a_guess=0.0, a_prime_guess=0.0, 
                                  max_iterations=100, tolerance=1e-5, 
                                  operational_characteristics=None, 
                                  operational_condition=None):
        """
        Computes the induction factors for a blade element at given radius.

        Args:
            radius (float): Radial position to compute induction factors for
            a_guess (float): Initial guess for axial induction factor
            a_prime_guess (float): Initial guess for tangential induction factor
            max_iterations (int): Maximum number of iterations
            tolerance (float): Convergence tolerance
            operational_characteristics: Operational characteristics of the turbine
            operational_condition: Current operational condition

        Returns:
            dict: Dictionary containing computed values including induction factors,
                  angles, and force coefficients
        """
        a = a_guess
        a_prime = a_prime_guess
        wind_speed = operational_condition.wind_speed
        omega = operational_condition.omega
        r = radius

        # Find the two nearest blade elements for interpolation
        sorted_elements = sorted(self.blade.elements, key=lambda x: x.r)
        radii = np.array([elem.r for elem in sorted_elements])
        
        # Find bracketing elements
        idx = np.searchsorted(radii, r)
        if idx == 0:
            elem1 = sorted_elements[0]
            elem2 = sorted_elements[0]
            w = 1.0
        elif idx >= len(sorted_elements):
            elem1 = sorted_elements[-1]
            elem2 = sorted_elements[-1]
            w = 1.0
        else:
            elem1 = sorted_elements[idx-1]
            elem2 = sorted_elements[idx]
            # Calculate interpolation weight
            w = (r - elem1.r) / (elem2.r - elem1.r)

        # Interpolate geometric properties
        chord = (1-w) * elem1.chord + w * elem2.chord
        twist_rad = np.radians((1-w) * elem1.twist + w * elem2.twist)

        # Get pitch angle through interpolation
        wind_speeds = np.array([op.wind_speed for op in operational_characteristics.characteristics])
        pitches = np.array([np.radians(op.pitch) for op in operational_characteristics.characteristics])
        pitch_rad = np.interp(operational_condition.wind_speed, wind_speeds, pitches)

        # Iterative solution
        for _ in range(max_iterations):
            # Calculate flow angle
            phi = np.arctan2((1-a) * wind_speed, (1+a_prime) * omega * r)
            
            # Calculate angle of attack
            alpha = phi - (pitch_rad + twist_rad)
            alpha_deg = np.degrees(alpha)

            # Get Cl and Cd through double interpolation
            cl1, cd1 = self._get_aero_coeffs_from_element(elem1, alpha_deg)
            cl2, cd2 = self._get_aero_coeffs_from_element(elem2, alpha_deg)
            
            # Interpolate between elements
            Cl = (1-w) * cl1 + w * cl2
            Cd = (1-w) * cd1 + w * cd2

            # Calculate force coefficients
            Cn = Cl * np.cos(phi) + Cd * np.sin(phi)
            Ct = Cl * np.sin(phi) - Cd * np.cos(phi)

            # Calculate solidity
            solidity = self.calculate_solidity(operational_conditions=operational_condition, 
                                             chord=chord, r=r)

            # Update induction factors
            a_new = 1 / ((4 * np.sin(phi)**2) / (solidity * Cn) + 1)
            a_prime_new = 1 / ((4 * np.sin(phi) * np.cos(phi)) / (solidity * Ct) - 1)

            # Check convergence
            if abs(a - a_new) < tolerance and abs(a_prime - a_prime_new) < tolerance:
                break

            a, a_prime = a_new, a_prime_new

        return {
            'radius': r,
            'a': a,
            'a_prime': a_prime,
            'alpha': alpha_deg,
            'cl': Cl,
            'cd': Cd,
            'phi': np.degrees(phi),
            'Cn': Cn,
            'Ct': Ct
        }

    def _get_aero_coeffs_from_element(self, element, alpha):
        """
        Helper method to get interpolated lift and drag coefficients from an element's airfoil data.
        
        Args:
            element (BladeElement): The blade element containing airfoil data
            alpha (float): Angle of attack in degrees
        
        Returns:
            tuple: (cl, cd) Interpolated lift and drag coefficients
        """
        if element.airfoil and element.airfoil.aero_data:
            alphas = np.array([data.alpha for data in element.airfoil.aero_data])
            cls = np.array([data.cl for data in element.airfoil.aero_data])
            cds = np.array([data.cd for data in element.airfoil.aero_data])
            
            return (np.interp(alpha, alphas, cls),
                    np.interp(alpha, alphas, cds))
        
        return 0.0, 0.0

    def compute_aerodynamic_performance(self, operational_condition: OperationalCondition):
        """
        Compute the aerodynamic performance of the blade.

        This method calculates the forces and moments acting on each blade element,
        as well as the total thrust, torque, power, and performance coefficients (CT and CP).

        Parameters:
        - blade (Blade): Blade object containing elements and operational conditions.

        Returns:
        - tuple: (total_thrust, total_torque, total_power, CT, CP)
          where:
            - total_thrust: Total thrust force acting on the rotor (N).
            - total_torque: Total torque generated by the rotor (Nm).
            - total_power: Total power generated by the rotor (W).
            - CT: Thrust coefficient (dimensionless).
            - CP: Power coefficient (dimensionless).
        """
        total_thrust = 0
        total_torque = 0

        # Get rotor properties
        R = self.blade.R
        A = np.pi * R**2  # Rotor area
        wind_speed = operational_condition.wind_speed  # Free stream velocity
        omega = operational_condition.omega  # Rotor angular velocity
        rho = operational_condition.rho  # Air density

        for element in self.blade.elements:
            # Get element properties
            r = element.r
            dr = element.dr
            alpha = element.alpha 
            phi = element.phi
            chord = element.chord
            Cl = element.cl
            Cd = element.cd
            a = element.a
            a_prime = element.a_prime

            # Calculate relative wind speed
            V_rel = np.sqrt(
                ((1 - a) * wind_speed)**2 + 
                ((1 + a_prime) * omega * r)**2
            )
            
            # Calculate lift and drag forces per unit length
            L = 0.5 * rho * V_rel**2 * chord * Cl
            D = 0.5 * rho * V_rel**2 * chord * Cd
            
            # Project forces to normal and tangential directions
            Fn = L * np.cos(phi) + D * np.sin(phi)
            Ft = L * np.sin(phi) - D * np.cos(phi)
            
            # Compute local contributions to thrust and torque
            dT = 4 * np.pi * r * rho * wind_speed**2 * a * (1 - a) * dr
            dM = 4 * np.pi * r**3 * rho * wind_speed * omega * a_prime * (1 - a) * dr
            
            # Store forces in element
            element.L = L
            element.D = D
            element.Fn = Fn
            element.Ft = Ft
            element.dT = dT
            element.dM = dM
            element.V_rel = V_rel

            # Add to totals
            total_thrust += dT
            total_torque += dM

        # Calculate total power
        total_power = total_torque * omega
        
        # Calculate coefficients
        denom_T = 0.5 * rho * A * wind_speed**2
        denom_P = 0.5 * rho * A * wind_speed**3
        
        ct = total_thrust / denom_T if denom_T != 0 else 0
        cp = total_power / denom_P if denom_P != 0 else 0

        return total_thrust, total_torque, total_power, ct, cp

