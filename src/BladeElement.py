from typing import Optional
import numpy as np

class BladeElement:
    def __init__(self, r: float, twist: float, chord: float, airfoil_id: int, airfoil: Optional['Airfoil'] = None):

        self.r = r                      # Spanwise position [m]
        self.twist = twist              # Twist angle [deg]
        self.chord = chord              # Chord length [m]
        self.airfoil_id = airfoil_id    # Airfoil index from file
        self.airfoil = airfoil          # Will be assigned later (optional)
        self.a = None                  # Axial induction factor (initial guess)
        self.a_prime = None            # Tangential induction factor (initial guess)
        self.Cn = None                 # Normal force coefficient (initial guess)
        self.Ct = None                 # Tangential force coefficient (initial guess)
        self.cl = None                 # Lift coefficient [1]
        self.cd = None                 # Drag coefficient [1]
        self.alpha = None              # Angle of attack [rad]
        self.phi = None                # Flow angle [rad]
        self.dr = None                 # Elemental radius [m]
        self.dT = None                 # Elemental thrust [N]
        self.dM = None                 # Elemental moment [Nm]
        self.L = None                  # Lift force [N]
        self.D = None                  # Drag forces [N]
        self.Fn = None                 # Normal force [N]
        self.Ft = None                 # Tangential force [N]
        self.V_rel = None              # Relative wind speed [m/s]
        
        self.solidity = self.calculate_solidity()  # Calculate solidity based on the number of blades and chord length


    def calculate_solidity(self, operational_conditions=None):
        """
        Calculate the solidity of the blade element.

        Returns:
        - solidity (float): Solidity of the blade element.
        """
        num_blades = operational_conditions.num_blades           # Number of blades (default value)

        if self.r == 0:
            return 1
        solidity = (num_blades * self.chord) / (2 * np.pi * self.r)
        return min(solidity, 1) #solidity can't exceed 1 for physical reasons
    

    def compute_element_induction_factors(self, a, a_prime, wind_speed, omega, r, phi, Cn, Ct, tolerance=1e-5, max_iterations=100):
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
        solidity = self.solidity

        for _ in range(self.max_iterations):

            phi = np.arctan2((1 - a) * wind_speed, 
                        (1 + a_prime) * omega * r)
            
            # Update axial induction factor
            a_new = 1 / (1 + (4 * np.sin(phi)**2) / (solidity * Cn))
            
            # Update tangential induction factor
            a_prime_new = 1 / (1 + (4 * np.sin(phi) * np.cos(phi)) / (solidity * Ct))
            
            # Check for convergence
            if abs(a - a_new) < self.tolerance and abs(a_prime - a_prime_new) < self.tolerance:
                break
            
            a, a_prime = a_new, a_prime_new

        return a, a_prime

    def compute_induction_factors(self, a_guess=0.0, a_prime_guess=0.0, max_iterations=100, tolerance=1e-5, operational_characteristics=None, operational_condition=None):
        """
        Compute induction factors for all blade elements.

        Returns:
        - list: List of tuples containing (a, a_prime) for each blade element
        """
        a = a_guess
        a_prime = a_prime_guess
        wind_speed = operational_condition.wind_speed
        omega = operational_condition.omega
        r = self.r
        
        # Get lift and drag coefficients from airfoil data
        if self.airfoil and self.airfoil.aero_data:
            # Calculate angle of attack
            twist_rad = np.radians(self.twist)
            
            # Interpolate pitch angle based on wind speed
            wind_speeds = np.array([op.wind_speed for op in self.blade.operational_characteristics])
            pitches = np.array([np.radians(op.pitch) for op in self.blade.operational_characteristics])
            pitch_rad = np.interp(operational_condition.wind_speed, wind_speeds, pitches)
            
            alpha = phi - (pitch_rad + twist_rad)
            
            # Interpolate Cl and Cd based on alpha in aero data
            aero_data = self.airfoil.aero_data
            alphas = np.array([data.alpha for data in aero_data])
            cls = np.array([data.cl for data in aero_data])
            cds = np.array([data.cd for data in aero_data])
            
            Cl = np.interp(np.degrees(alpha), alphas, cls)
            Cd = np.interp(np.degrees(alpha), alphas, cds)
            
            # Calculate normal and tangential coefficients
            Cn = Cl * np.cos(phi) + Cd * np.sin(phi)
            Ct = Cl * np.sin(phi) - Cd * np.cos(phi)
            
            # Compute induction factors for this element
            a, a_prime = self.compute_element_induction_factors(a, a_prime, wind_speed, omega, r, phi, Cn, Ct, tolerance=1e-5, max_iterations=100)

            phi = np.arctan2((1 - a) * wind_speed, 
                (1 + a_prime) * omega * r)
            
            self.alpha = alpha
            self.cl = Cl
            self.cd = Cd
            self.a = a
            self.a_prime = a_prime
            self.phi = phi
            self.Cn = Cn
            self.Ct = Ct


    def __repr__(self):
        return (f"BladeElement(r={self.r}, twist={self.twist}, chord={self.chord}, "
                f"airfoil_id={self.airfoil_id}, airfoil={'Assigned' if self.airfoil else 'None'})")