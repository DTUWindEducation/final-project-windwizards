from typing import Optional

class BladeElement:
    def __init__(self, r: float, twist: float, chord: float, airfoil_id: int, airfoil: Optional['Airfoil'] = None, num_blades: int = 3):

        self.r = r                      # Spanwise position [m]
        self.twist = twist              # Twist angle [deg]
        self.chord = chord              # Chord length [m]
        self.airfoil_id = airfoil_id    # Airfoil index from file
        self.airfoil = airfoil          # Will be assigned later (optional)
        self.num_blades = num_blades           # Number of blades (default value)
        self.solidity = self.calculate_solidity()  # Calculate solidity based on the number of blades and chord length

    def calculate_solidity(self):
        """
        Calculate the solidity of the blade element.

        Returns:
        - solidity (float): Solidity of the blade element.
        """
        return (self.num_blades * self.chord) / (2 * np.pi * self.r)

    def __repr__(self):
        return (f"BladeElement(r={self.r}, twist={self.twist}, chord={self.chord}, "
                f"airfoil_id={self.airfoil_id}, airfoil={'Assigned' if self.airfoil else 'None'})")