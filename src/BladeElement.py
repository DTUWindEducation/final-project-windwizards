from typing import Optional
import numpy as np

class BladeElement:
    def __init__(self, r: float, twist: float, chord: float, airfoil_id: int, airfoil: Optional['Airfoil'] = None, num_blades: int = 3):

        self.r = r                      # Spanwise position [m]
        self.twist = twist              # Twist angle [deg]
        self.chord = chord              # Chord length [m]
        self.airfoil_id = airfoil_id    # Airfoil index from file
        self.airfoil = airfoil          # Will be assigned later (optional)
        self.a = 0.0                  # Axial induction factor (initial guess)
        self.a_prime = 0.0            # Tangential induction factor (initial guess)
        self.Cn = 0.0                 # Normal force coefficient (initial guess)
        self.Ct = 0.0                 # Tangential force coefficient (initial guess)
        self.cl = 0.0               # Lift coefficient [1]
        self.cd = 0.0               # Drag coefficient [1]
        self.alpha = 0.0               # Angle of attack [rad]
        self.phi = 0.0                 # Flow angle [rad]
        self.dr = 0.0                 # Elemental radius [m]
        self.dT = 0.0                 # Elemental thrust [N]
        self.dM = 0.0                  # Elemental moment [Nm]
        self.L = 0.0               # Lift force [N]
        self.D = 0.0               # Drag forces [N]
        self.Fn = 0.0               # Normal force [N]
        self.Ft = 0.0               # Tangential force [N]
        self.V_rel = 0.0               # Relative wind speed [m/s]
        self.num_blades = num_blades           # Number of blades (default value)
        self.solidity = self.calculate_solidity()  # Calculate solidity based on the number of blades and chord length

    def calculate_solidity(self):
        """
        Calculate the solidity of the blade element.

        Returns:
        - solidity (float): Solidity of the blade element.
        """
        if self.r == 0:
            return 1
        solidity = (self.num_blades * self.chord) / (2 * np.pi * self.r)
        return min(solidity, 1) #solidity can't exceed 1 for physical reasons


    def __repr__(self):
        return (f"BladeElement(r={self.r}, twist={self.twist}, chord={self.chord}, "
                f"airfoil_id={self.airfoil_id}, airfoil={'Assigned' if self.airfoil else 'None'})")