from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from src.Airfoil import Airfoil
from src.BladeElement import BladeElement
from src.OperationalCharacteristics import OperationalCharacteristics


class Blade:
    def __init__(self, elements: List[BladeElement] = None, operational_characteristics: OperationalCharacteristics = None):
        """
        Initialize the Blade class.

        Parameters:
        - elements (List[BladeElement]): List of blade elements.
        - num_blades (int): Number of blades.
        - operational_conditions (Optional[Dict]): Dictionary containing operational conditions.
        """
        self.elements = elements if elements else []
        self.R = max(element.r for element in self.elements) if self.elements else 0  # Tip radius
        self.operational_characteristics = operational_characteristics
        
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
                airfoil_id = (int(parts[6])-1) # Airfoil index
            except ValueError:
                continue

            airfoil = airfoil_map.get(airfoil_id) if airfoil_map else None
            element = BladeElement(r=r, twist=twist, chord=chord, airfoil_id=airfoil_id, airfoil=airfoil)
            self.elements.append(element)

    def calculate_element_discretization_lengths(self):
        """Calculate and assign the discretization length (dr) for each blade element."""
        if not self.elements:
            raise ValueError("No blade elements found. Please load blade data first for the function to work.")

        for i, element in enumerate(self.elements):
            if i == 0:  # First element
                dr = (self.elements[i + 1].r - element.r) / 2
            elif i == len(self.elements) - 1:  # Last element
                dr = (element.r - self.elements[i - 1].r) / 2
            else:  # Middle elements
                dr = (self.elements[i + 1].r - self.elements[i - 1].r) / 2
            element.dr = dr

    def compute_induction_factors_blade(self, a_guess=0.0, a_prime_guess=0.0, max_iterations=100, tolerance=1e-5, operational_condition=None):
        """
        Compute induction factors for all blade elements.

        Parameters:
        - a_guess (float): Initial guess for axial induction factor.
        - a_prime_guess (float): Initial guess for tangential induction factor.
        - max_iterations (int): Maximum number of iterations for convergence.
        - tolerance (float): Convergence tolerance.

        Returns:
        - List[BladeElement]: List of blade elements with updated induction factors.
        """
        self.calculate_element_discretization_lengths()  # Calculate dr for each element
        
        for element in self.elements:
            element.calculate_solidity(operational_conditions=operational_condition)  # Calculate solidity for each element
            element.compute_induction_factors(a_guess=a_guess, a_prime_guess=a_prime_guess,max_iterations=max_iterations, tolerance=tolerance, operational_characteristics=self.operational_characteristics, operational_condition=operational_condition)
            
        return self.elements

    def __repr__(self):
        return f"Blade with {len(self.elements)} elements, {self.num_blades} blades, and operational conditions: {self.operational_conditions}"
    
    def __str__(self):
        return (f"Blade:\n"
                f"  Number of Elements: {len(self.elements)}\n"
                f"  Tip Radius: {self.R} m\n"
                f"  Operational Characteristics: {self.operational_characteristics}\n")