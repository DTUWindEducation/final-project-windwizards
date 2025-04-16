from dataclasses import dataclass
from typing import Optional

@dataclass
class BladeElement:
    r: float                      # Spanwise position [m]
    twist: float                  # Twist angle [deg]
    chord: float                  # Chord length [m]
    airfoil_id: int               # Airfoil index from file
    airfoil: Optional[Airfoil] = None  # Will be assigned later