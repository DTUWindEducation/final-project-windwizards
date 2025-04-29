from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from mpl_toolkits.mplot3d import Axes3D
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
        self.R = None  # Tip radius
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
            self.R = max(element.r for element in self.elements)
            element.compute_induction_factors(a_guess=a_guess, a_prime_guess=a_prime_guess,max_iterations=max_iterations, tolerance=tolerance, operational_characteristics=self.operational_characteristics, operational_condition=operational_condition)
            
        
        return self.elements
    
    
    def plot_blade_shape(self, scale_factor=10):
        """
        Plot the blade shape in 3D.
        
        Parameters:
        - scale_factor (float): Factor to scale the chordwise and thickness dimensions
                               for better visualization. Default is 5.
        """
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # For coloring the blade elements
        colors = cm.viridis(np.linspace(0, 1, len(self.elements)))
        
        for i, element in enumerate(self.elements):
            if element.airfoil and hasattr(element.airfoil, 'shape_coords'):
                # Extract airfoil coordinates and scale by chord
                airfoil_coords = np.array(element.airfoil.shape_coords)
                x = airfoil_coords[:, 0] * element.chord
                y = np.zeros_like(x)  # Initial y is zero
                z = airfoil_coords[:, 1] * element.chord
                
                # Apply twist (rotation around y-axis)
                twist_rad = np.radians(element.twist)
                x_rotated = x * np.cos(twist_rad) - z * np.sin(twist_rad)
                z_rotated = x * np.sin(twist_rad) + z * np.cos(twist_rad)
                
                # Position at correct radial location
                y_final = y + element.r
                
                # Plot the airfoil profile as a line
                ax.plot(x_rotated, y_final, z_rotated, color=colors[i], 
                       label=f'r/R={element.r:.2f}' if i % 3 == 0 else "")
                
                # Connect to next element if not the last one
                if i < len(self.elements) - 1 and i % 2 == 0:
                    next_element = self.elements[i+1]
                    if next_element.airfoil and hasattr(next_element.airfoil, 'shape_coords'):
                        # Calculate leading and trailing edge points for current and next element
                        le_current = [x_rotated[0], y_final[0], z_rotated[0]]
                        te_current = [x_rotated[-1], y_final[-1], z_rotated[-1]]
                        
                        next_coords = np.array(next_element.airfoil.shape_coords)
                        next_x = next_coords[:, 0] * next_element.chord
                        next_z = next_coords[:, 1] * next_element.chord
                        next_twist_rad = np.radians(next_element.twist)
                        next_x_rotated = next_x * np.cos(next_twist_rad) - next_z * np.sin(next_twist_rad)
                        next_z_rotated = next_x * np.sin(next_twist_rad) + next_z * np.cos(next_twist_rad)
                        
                        le_next = [next_x_rotated[0], next_element.r, next_z_rotated[0]]
                        te_next = [next_x_rotated[-1], next_element.r, next_z_rotated[-1]]
                        
                        # Draw lines between leading and trailing edges
                        ax.plot([le_current[0], le_next[0]], [le_current[1], le_next[1]], [le_current[2], le_next[2]], 'k-')
                        ax.plot([te_current[0], te_next[0]], [te_current[1], te_next[1]], [te_current[2], te_next[2]], 'k-')
        
        # Set equal aspect ratio with scale factor for better visibility
        ax.set_box_aspect([scale_factor, self.R, scale_factor])
        ax.set_title('Blade Shape')
        ax.set_xlabel('X (Chordwise direction)')
        ax.set_ylabel('Y (Spanwise direction)')
        ax.set_zlabel('Z (Thickness direction)')
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()

        
    

    def __repr__(self):
        return f"Blade with {len(self.elements)} elements, {self.num_blades} blades, and operational conditions: {self.operational_conditions}"
    
    def __str__(self):
        return (f"Blade:\n"
                f"  Number of Elements: {len(self.elements)}\n"
                f"  Tip Radius: {self.R} m\n"
                f"  Operational Characteristics: {self.operational_characteristics}\n")