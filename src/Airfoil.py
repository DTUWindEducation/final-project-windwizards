from pathlib import Path
from typing import List, Optional, Tuple
import matplotlib.pyplot as plt


class AeroCoefficients:
    """
    Represents aerodynamic coefficients for an airfoil at a specific angle of attack.

    Attributes:
        alpha (float): Angle of attack in degrees.
        cl (float): Lift coefficient.
        cd (float): Drag coefficient.
        cm (float): Moment coefficient.
    """

    def __init__(self, alpha: float, cl: float, cd: float, cm: float):
        """
        Initializes an AeroCoefficients object.

        Args:
            alpha (float): Angle of attack in degrees.
            cl (float): Lift coefficient.
            cd (float): Drag coefficient.
            cm (float): Moment coefficient.
        """
        self.alpha = alpha
        self.cl = cl
        self.cd = cd
        self.cm = cm


class Airfoil:
    """
    Represents an airfoil with its shape and aerodynamic data.

    Attributes:
        name (str): Name of the airfoil.
        reynolds (float): Reynolds number.
        control (int): Control parameter.
        incl_ua_data (bool): Whether unsteady aerodynamic data is included.
        ref_coord (Tuple[float, float]): Reference coordinate of the airfoil.
        shape_coords (List[Tuple[float, float]]): List of shape coordinates (x, y).
        aero_data (List[AeroCoefficients]): List of aerodynamic coefficients.
    """

    def __init__(
        self,
        name: str,
        reynolds: float,
        control: int,
        incl_ua_data: bool,
        ref_coord: Optional[Tuple[float, float]] = None,
        shape_coords: Optional[List[Tuple[float, float]]] = None,
        aero_data: Optional[List[AeroCoefficients]] = None,
    ):
        """
        Initializes an Airfoil object.

        Args:
            name (str): Name of the airfoil.
            reynolds (float): Reynolds number.
            control (int): Control parameter.
            incl_ua_data (bool): Whether unsteady aerodynamic data is included.
            ref_coord (Optional[Tuple[float, float]]): Reference coordinate of the airfoil.
            shape_coords (Optional[List[Tuple[float, float]]]): List of shape coordinates (x, y).
            aero_data (Optional[List[AeroCoefficients]]): List of aerodynamic coefficients.
        """
        self.name = name
        self.reynolds = reynolds
        self.control = control
        self.incl_ua_data = incl_ua_data
        self.ref_coord = ref_coord if ref_coord else (0.0, 0.0)
        self.shape_coords = shape_coords if shape_coords else []
        self.aero_data = aero_data if aero_data else []

    def load_from_file(self, file_path: Path):
        """
        Loads airfoil shape data from a file.

        Args:
            file_path (Path): Path to the file containing airfoil data.
        """
        match = file_path.stem.split("AF")
        number = match[1] if len(match) > 1 else "??"
        self.name = f"Airfoil {number}"
        lines = file_path.read_text(encoding="utf-8").splitlines()

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
                    except ValueError:
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
                i += num_coords - 1

            elif "NumCoords" in line:
                try:
                    num_coords = int(line.split()[0])
                except ValueError:
                    pass

            i += 1

    def load_from_polar_and_coords(self, coord_path: Path, polar_path: Path):
        """
        Loads airfoil shape and aerodynamic data from coordinate and polar files.

        Args:
            coord_path (Path): Path to the file containing shape coordinates.
            polar_path (Path): Path to the file containing aerodynamic data.
        """
        self.load_from_file(coord_path)

        self.aero_data = []
        self.reynolds = 0.0
        self.control = 0
        self.incl_ua_data = False
        parsing_data = False

        lines = polar_path.read_text(encoding="utf-8").splitlines()

        for line in lines:
            stripped = line.strip()

            if "! Reynolds number in millions" in stripped:
                try:
                    self.reynolds = float(stripped.split()[0]) * 10**6
                except ValueError:
                    pass

            elif "Ctrl" in stripped:
                try:
                    self.control = int(stripped.split()[0])
                except ValueError:
                    pass

            elif "InclUAdata" in stripped:
                self.incl_ua_data = stripped.split()[0].lower() == "true"

            elif "NumAlf" in stripped:
                parsing_data = True
                continue

            if parsing_data:
                if stripped.lower().startswith("alpha") or stripped.startswith("("):
                    continue

                parts = stripped.split()
                if len(parts) < 4:
                    continue

                try:
                    alpha, cl, cd, cm = map(float, parts[:4])
                    self.aero_data.append(AeroCoefficients(alpha, cl, cd, cm))
                except ValueError:
                    continue

    def __repr__(self):
        """
        Returns a string representation of the Airfoil object.

        Returns:
            str: String representation of the Airfoil object.
        """
        return (
            f"Airfoil(name={self.name}, reynolds={self.reynolds}, control={self.control}, "
            f"incl_ua_data={self.incl_ua_data}, ref_coord={self.ref_coord}, "
            f"num_shape_coords={len(self.shape_coords)}, num_aero_data={len(self.aero_data)})"
        )


def plot_airfoil_shapes(airfoils: List[Airfoil], indices: List[int]):
    """
    Plots the shapes of multiple airfoils.

    Args:
        airfoils (List[Airfoil]): List of Airfoil objects to plot.
        indices (List[int]): Indices of the airfoils to plot.
    """
    plt.figure(figsize=(10, 6))

    for idx in indices:
        airfoil = airfoils[idx]
        x, y = zip(*airfoil.shape_coords)
        plt.plot(x, y, label=f"{airfoil.name}")

    plt.axis("equal")
    plt.title("Airfoil Shapes")
    plt.xlabel("x/c")
    plt.ylabel("y/c")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
