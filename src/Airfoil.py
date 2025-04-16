import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# Define AeroCoefficients class
@dataclass
class AeroCoefficients:
    alpha: float
    cl: float
    cd: float
    cm: float

# Define the Airfoil class
@dataclass
class Airfoil:
    name: str
    reynolds: float
    control: int
    incl_ua_data: bool
    ref_coord: Optional[Tuple[float, float]] = None
    shape_coords: List[Tuple[float, float]] = field(default_factory=list)
    aero_data: List[AeroCoefficients] = field(default_factory=list)

    @classmethod
    def from_file(cls, file_path: Path) -> "Airfoil":
        name = file_path.stem
        lines = file_path.read_text(encoding='utf-8').splitlines()

        reynolds = 0.0
        control = 0
        incl_ua_data = False
        aero_data = []
        ref_coord = None
        shape_coords = []
        num_coords = 0

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if "Re" in line:
                try:
                    reynolds = float(line.split()[0])
                except ValueError:
                    pass

            elif "Ctrl" in line:
                control = int(line.split()[0])

            elif "InclUAdata" in line:
                incl_ua_data = line.split()[0].lower() == "true"

            elif "NumCoords" in line:
                try:
                    num_coords = int(line.split()[0])
                except ValueError:
                    pass

            elif "! x-y coordinate of airfoil reference" in line:
                if i + 1 < len(lines):
                    try:
                        x, y = map(float, lines[i + 1].strip().split())
                        ref_coord = (x, y)
                        i += 1
                    except Exception:
                        pass

            elif "! coordinates of airfoil shape" in line:
                for j in range(i + 2, i + 2 + (num_coords)):
                    if j < len(lines):
                        parts = lines[j].strip().split()
                        if len(parts) == 2:
                            try:
                                x, y = map(float, parts)
                                shape_coords.append((x, y))
                            except ValueError:
                                pass
                i += (num_coords - 1)

            elif "NumAlf" in line:
                try:
                    num_alf = int(line.split()[0])
                    for j in range(i + 2, i + 2 + num_alf):
                        parts = lines[j].strip().split()
                        try:
                            if len(parts) >= 4:
                                alpha, cl, cd, cm = map(float, parts[:4])
                                aero_data.append(AeroCoefficients(alpha, cl, cd, cm))
                        except ValueError:
                            pass
                    i += num_alf
                except Exception:
                    pass

            i += 1

        return cls(
            name=name,
            reynolds=reynolds,
            control=control,
            incl_ua_data=incl_ua_data,
            ref_coord=ref_coord,
            shape_coords=shape_coords,
            aero_data=aero_data
        )

    @classmethod
    def from_polar_and_coords(cls, coord_path: Path, polar_path: Path) -> "Airfoil":
        airfoil = cls.from_file(coord_path)
        
        lines = polar_path.read_text(encoding='utf-8').splitlines()
        aero_data = []

        for line in lines:
            line = line.strip()
            if not line or any(line.startswith(c) for c in ("-", "=", "!", "#", "D")):
                continue

            parts = line.split()
            try:
                if len(parts) >= 4:
                    alpha, cl, cd, cm = map(float, parts[:4])
                    aero_data.append(AeroCoefficients(alpha, cl, cd, cm))
            except ValueError:
                continue

        airfoil.aero_data = aero_data
        return airfoil

# Function for plotting airfoil shapes
def plot_airfoil_shapes(airfoil_dir: Path, indices: list):
    plt.figure(figsize=(10, 6))
    
    for idx in indices:
        # Create file names for the coordinate and polar files
        coord_filename = f"IEA-15-240-RWT_AF{idx:02d}_Coords.txt"
        polar_filename = f"IEA-15-240-RWT_AeroDyn15_Polar_{idx:02d}.dat"
        
        # Paths to the files
        coord_path = airfoil_dir / coord_filename
        polar_path = airfoil_dir / polar_filename
        
        # Load the airfoil using the from_polar_and_coords method
        airfoil = Airfoil.from_polar_and_coords(coord_path, polar_path)
        
        # Extract (x, y) coordinates from the airfoil object
        x, y = zip(*airfoil.shape_coords)
        
        # Plot airfoil coordinates
        plt.plot(x, y, label=f'AF{idx:02d}')
    
    # Plot settings
    plt.axis('equal')
    plt.title('Airfoil Shapes')
    plt.xlabel('x/c')
    plt.ylabel('y/c')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
