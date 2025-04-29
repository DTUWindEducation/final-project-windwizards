import pytest
import numpy as np
from pathlib import Path
import sys

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.Blade import Blade
from src.Airfoil import Airfoil

def test_bladeelement_solidity():
    # Setup
    base_path = Path(__file__).parent.parent / "inputs/IEA-15-240-RWT"
    blade_file = base_path / "IEA-15-240-RWT_AeroDyn15_blade.dat"
    
    # Create airfoil map (needed for blade loading)
    airfoil_map = {}
    idx = "49"
    coord_file = base_path / f"Airfoils/IEA-15-240-RWT_AF{idx}_Coords.txt"
    polar_file = base_path / f"Airfoils/IEA-15-240-RWT_AeroDyn15_Polar_{idx}.dat"
    airfoil = Airfoil(name="", reynolds=0.0, control=0, incl_ua_data=False)
    airfoil.load_from_polar_and_coords(coord_file, polar_file)
    airfoil_map[49] = airfoil

    # Load blade
    blade = Blade()
    blade.load_from_file(blade_file, airfoil_map)
    
    # Get the last element (index 49)
    element_49 = blade.elements[-1]
    
    # Calculate expected solidity
    # σ(r) = (c(r)B)/(2πr) where B is number of blades (3)
    expected_solidity = (element_49.chord * 3) / (2 * np.pi * element_49.r)
    
    # Get actual solidity
    actual_solidity = element_49.solidity
    
    # Assert with some tolerance due to floating point arithmetic
    assert abs(actual_solidity - expected_solidity) < 1e-10, \
        f"Expected solidity {expected_solidity}, but got {actual_solidity}"

if __name__ == "__main__":
    pytest.main([__file__])