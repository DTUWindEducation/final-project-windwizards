from pathlib import Path
from typing import List, Dict
from .Airfoil import Airfoil
from .BladeElement import BladeElement

class Blade:
    def __init__(self, elements: List[BladeElement] = None):
        self.elements = elements if elements else []

    def load_from_file(self, file_path: Path, airfoil_map: Dict[int, Airfoil] = None):
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

    def __repr__(self):
        return f"Blade with {len(self.elements)} elements"