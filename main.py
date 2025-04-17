from pathlib import Path
from src.Airfoil import Airfoil, plot_airfoil_shapes
from src.Blade import Blade
from src.OperationalConditions import OperationalConditions

# Set the base path
base_path = Path(__file__).parent / "inputs/IEA-15-240-RWT"

# Load airfoils into a dictionary
print("Loading airfoils...")
airfoil_map = {}

for i in range(50):
    idx = f"{i:02d}"
    coord_file = base_path / f"Airfoils/IEA-15-240-RWT_AF{idx}_Coords.txt"
    polar_file = base_path / f"Airfoils/IEA-15-240-RWT_AeroDyn15_Polar_{idx}.dat"

    # Create Airfoil object and load data from the files
    airfoil = Airfoil(name="", reynolds=0.0, control=0, incl_ua_data=False)
    airfoil.load_from_polar_and_coords(coord_file, polar_file)
    
    # Store the Airfoil in the map
    airfoil_map[i] = airfoil

print(f"Loaded {len(airfoil_map)} airfoils")

# Load blade data
print("Loading blade...")
blade_file = base_path / "IEA-15-240-RWT_AeroDyn15_blade.dat"
blade = Blade()
blade.load_from_file(blade_file, airfoil_map)
print(f"Loaded blade with {len(blade.elements)} elements")

# Load operational conditions
print("Loading operational conditions...")
opt_file = base_path / "IEA_15MW_RWT_Onshore.opt"
ops = OperationalConditions()
ops.load_from_file(opt_file)
print(f"Loaded {len(ops.conditions)} operational conditions")

# Display first blade element and operational condition
print("\nFirst blade element:")
print(blade.elements[0])

print("\nFirst operational condition:")
print(ops.conditions[0])

# Display first airfoil summary
print("\nFirst airfoil summary:")
print(airfoil_map[0])

# Plot selected airfoil shapes
print("\nPlotting selected airfoil shapes...")
airfoil_indices = [0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49]
plot_airfoil_shapes(list(airfoil_map.values()), airfoil_indices)
