from pathlib import Path
from src.Airfoil import Airfoil, plot_airfoil_shapes
from src.Blade import Blade
from src.OperationalCharacteristics import OperationalCharacteristics, OperationalCharacteristic
from src.OperationalCondition import OperationalCondition
from src.BladeElementTheory import BladeElementTheory

import numpy as np

# Set the base path
base_path = Path(__file__).parent / "inputs/IEA-15-240-RWT"


# Loading Data ________________________________________________________________


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

# Load operational conditions
print("Loading operational conditions...")
opt_file = base_path / "IEA_15MW_RWT_Onshore.opt"
ops = OperationalCharacteristics()
ops.load_from_file(opt_file)
print(f"Loaded {len(ops.characteristics)} operational conditions")

# Load blade data
print("Loading blade...")
blade_file = base_path / "IEA-15-240-RWT_AeroDyn15_blade.dat"
blade = Blade(operational_characteristics=ops)  # Initialize blade with operational characteristics
blade.load_from_file(file_path=blade_file,airfoil_map= airfoil_map)
print(f"Loaded blade with {len(blade.elements)} elements")
print(f"Blade characteristic: {blade.operational_characteristics} m")
ops.plot_characteristics(V_min=0, V_max=30, num_points=100)

# Processing  Data _____________________________________________________________

# Create operational condition object
operational_condition = OperationalCondition(wind_speed=10, rho=1.225, num_blades=3)
operational_condition.calculate_angular_velocity(blade=blade)
print(operational_condition)

# Calculate induction factors for each blade element
print("Calculating induction factors for each blade element...")
blade.compute_induction_factors_blade(operational_condition=operational_condition)

# Run blade element momentum theory
print("Running blade element momentum theory...")
bet = BladeElementTheory(blade=blade)
result = bet.compute_aerodynamic_performance(operational_condition=operational_condition)
print(f"Total Thrust: {result[0]} N")
print(f"Total Torque: {result[1]} Nm")
print(f"Total Power: {result[2]} W")
print(f"Thrust Coefficient (CT): {result[3]}")
print(f"Power Coefficient (CP): {result[4]}")



# # Display first blade element and operational condition
# print("\nFirst blade element:")
# print(blade.elements[0])

# print("\nFirst operational condition:")
# print(ops.characteristics[0])

# # Display first airfoil summary
# print("\nFirst airfoil summary:")
# print(airfoil_map[0])

# # Plot selected airfoil shapes
# print("\nPlotting selected airfoil shapes...")
# airfoil_indices = [0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49]
# plot_airfoil_shapes(list(airfoil_map.values()), airfoil_indices)