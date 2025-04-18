from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from .Airfoil import Airfoil
from .BladeElement import BladeElement

class Blade:
    def __init__(self, elements: List[BladeElement] = None, num_blades: int = 3, operational_conditions: Optional[Dict] = None):
        """
        Initialize the Blade class.

        Parameters:
        - elements (List[BladeElement]): List of blade elements.
        - num_blades (int): Number of blades.
        - operational_conditions (Optional[Dict]): Dictionary containing operational conditions (e.g., wind speed, RPM).
        """
        self.elements = elements if elements else []
        self.operational_conditions = operational_conditions if operational_conditions else {}
        self.num_blades = num_blades
        self.omega = self.operational_conditions.get('rpm', 0) * 2 * np.pi / 60  # Convert RPM to rad/s
        self.V = self.operational_conditions.get('wind_speed', 0)  # Wind speed [m/s]

    def load_from_file(self, file_path: Path, airfoil_map: Dict[int, Airfoil] = None):
        """
        Load blade elements from a file.

        Parameters:
        - file_path (Path): Path to the file containing blade element data.
        - airfoil_map (Dict[int, Airfoil]): Mapping of airfoil IDs to Airfoil objects.
        """
        lines = file_path.read_text(encoding='utf-8').splitlines()
        self.elements = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith(("-", "=", "!")):
                continue  # Skip comments or header lines

            parts = line.split()
            if len(parts) < 7:
                continue

            try:
                r = float(parts[0])          # Radius position
                twist = float(parts[4])      # Twist angle in degrees
                chord = float(parts[5])      # Chord length
                airfoil_id = int(parts[6])   # Airfoil index
            except ValueError:
                continue

            airfoil = airfoil_map.get(airfoil_id) if airfoil_map else None
            element = BladeElement(r=r, twist=twist, chord=chord, airfoil_id=airfoil_id, airfoil=airfoil)
            self.elements.append(element)

    def calculate_tip_speed_ratio(self, u_wind: float, omega: float):
        """
        Calculate the tip speed ratio (TSR) for the blade.

        Parameters:
        - u_wind (float): Wind speed [m/s].
        - omega (float): Rotational speed [rad/s].

        Returns:
        - TSR (float): Tip speed ratio.
        """
        if u_wind == 0:
            return 0
        r_tip = max(element.r for element in self.elements)  # Get the tip radius
        return (r_tip * omega) / u_wind

    def __repr__(self):
        return f"Blade with {len(self.elements)} elements, {self.num_blades} blades, and operational conditions: {self.operational_conditions}"