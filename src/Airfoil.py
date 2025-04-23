from pathlib import Path 
from typing import List, Optional, Tuple
from re import search
import matplotlib.pyplot as plt

# Define AeroCoefficients class
class AeroCoefficients:
    def __init__(self, alpha: float, cl: float, cd: float, cm: float):
        self.alpha = alpha
        self.cl = cl
        self.cd = cd
        self.cm = cm

# Define the Airfoil class
class Airfoil:
    def __init__(self, name: str, reynolds: float, control: int, incl_ua_data: bool,
                 ref_coord: Optional[Tuple[float, float]] = None,
                 shape_coords: Optional[List[Tuple[float, float]]] = None,
                 aero_data: Optional[List[AeroCoefficients]] = None):
        self.name = name
        self.reynolds = reynolds
        self.control = control
        self.incl_ua_data = incl_ua_data
        self.ref_coord = ref_coord if ref_coord else (0.0, 0.0)
        self.shape_coords = shape_coords if shape_coords else []
        self.aero_data = aero_data if aero_data else []

    def load_from_file(self, file_path: Path):
        match = search(r"AF(\d{2})", file_path.stem)
        number = match.group(1) if match else "??"
        self.name = f"Airfoil {number}"
        lines = file_path.read_text(encoding='utf-8').splitlines()

        self.ref_coord = None
        self.shape_coords = []
        num_coords = 0

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if "! x-y coordinate of airfoil reference" in line:
                if i + 2 < len(lines):
                    try:
                        x, y = map(float, lines[i + 2].strip().split())
                        self.ref_coord = (x, y)
                        i += 2
                    except Exception:
                        pass

            elif "! coordinates of airfoil shape" in line:
                for j in range(i + 2, i + 2 + num_coords):
                    if j < len(lines):
                        parts = lines[j].strip().split()
                        if len(parts) == 2:
                            try:
                                x, y = map(float, parts)
                                self.shape_coords.append((x, y))
                            except ValueError:
                                pass
                i += (num_coords - 1)

            elif "NumCoords" in line:
                try:
                    num_coords = int(line.split()[0])
                except ValueError:
                    pass

            i += 1

    def load_from_polar_and_coords(self, coord_path: Path, polar_path: Path):
        # Load shape coordinates from the file
        self.load_from_file(coord_path)
        
        # Read polar data for aerodynamic coefficients
        self.aero_data = []
        self.reynolds = 0.0
        self.control = 0
        self.incl_ua_data = False
        parsing_data = False

        lines = polar_path.read_text(encoding='utf-8').splitlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if "! Reynolds number in millions" in line:
                try:
                    self.reynolds = float(line.split()[0]) * 10**6
                except ValueError:
                    pass

            elif "Ctrl" in line:
                self.control = int(line.split()[0])

            elif "InclUAdata" in line:
                self.incl_ua_data = line.split()[0].lower() == "true"

            i += 1

        # Parse aerodynamic data (alpha, cl, cd, cm)
        for line in lines:
            stripped = line.strip()

            # Skip empty lines and comment lines
            if not stripped or stripped.startswith(("!", "#")):
                continue

            # Detect start of aerodynamic data section
            if "NumAlf" in stripped:
                parsing_data = True
                continue

            if parsing_data:
                # Skip header line if present
                if stripped.lower().startswith("alpha") or stripped.startswith("("):
                    continue

                parts = stripped.split()
                if len(parts) < 4:
                    continue  # not enough data to unpack

                try:
                    alpha, cl, cd, cm = map(float, parts[:4])
                    self.aero_data.append(AeroCoefficients(alpha, cl, cd, cm))
                except ValueError:
                    # If conversion fails, skip the line
                    continue

    def __repr__(self):
        return (f"Airfoil(name={self.name}, reynolds={self.reynolds}, control={self.control}, "
                f"incl_ua_data={self.incl_ua_data}, ref_coord={self.ref_coord}, "
                f"num_shape_coords={len(self.shape_coords)}, num_aero_data={len(self.aero_data)})")

def plot_airfoil_shapes(airfoils: List[Airfoil], indices: List[int]):
    plt.figure(figsize=(10, 6))
    
    for idx in indices:
        # Get the Airfoil from the list of loaded Airfoils
        airfoil = airfoils[idx]
        
        # Extract (x, y) coordinates from the Airfoil object
        x, y = zip(*airfoil.shape_coords)
        
        # Plot Airfoil coordinates
        plt.plot(x, y, label=f'{airfoil.name}')
    
    # Plot settings
    plt.axis('equal')
    plt.title('Airfoil Shapes')
    plt.xlabel('x/c')
    plt.ylabel('y/c')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

