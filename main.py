from pathlib import Path
from src.Airfoil import Airfoil, plot_airfoil_shapes
from src.Blade import Blade
from src.OperationalCharacteristics import OperationalCharacteristics, OperationalCharacteristic
from src.OperationalCondition import OperationalCondition
from src.BladeElementTheory import BladeElementTheory
from src.PerformanceAnalyzer import PerformanceAnalyzer
from src import save_results, save_plots

import numpy as np
import matplotlib.pyplot as plt



# Input _______________________________________________________________________

# Define operational conditions
wind_speed = 10.0  # Wind speed in m/s
rho = 1.225  # Air density in kg/m^3 (standard value at sea level)
num_blades = 3  # Number of blades

min_wind_speed = 0  # Minimum wind speed for performance analysis
max_wind_speed = 25  # Maximum wind speed for performance analysis
wind_speed_discretisation = 100  # Number of points for wind speed discretization

# Define the blade data source 
Data_Source = "IEA-15-240-RWT"  # Data source name


# Loading Data ________________________________________________________________

# Set the Data source base path
base_path = Path(__file__).parent / "inputs" / Data_Source

# Load airfoils into a dictionary
print("Loading airfoils...")
airfoil_map = {}

# Iterate through all coordinate files in the Airfoils directory
for coord_file in (base_path / "Airfoils").glob("IEA-15-240-RWT_AF*_Coords.txt"):
    # Extract the index from the filename
    idx = coord_file.stem.split('_')[-2][2:]
    polar_file = base_path / f"Airfoils/IEA-15-240-RWT_AeroDyn15_Polar_{idx}.dat"

    # Create Airfoil object and load data from the files
    airfoil = Airfoil(name="", reynolds=0.0, control=0, incl_ua_data=False)
    airfoil.load_from_polar_and_coords(coord_file, polar_file)
    
    # Store the Airfoil in the map
    airfoil_map[int(idx)] = airfoil

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
# ops.plot_characteristics(V_min=0, V_max=30, num_points=100)

# Processing  Data _____________________________________________________________

# Create operational condition object
operational_condition = OperationalCondition(wind_speed=wind_speed, rho=rho, num_blades=num_blades)
operational_condition.calculate_angular_velocity(blade=blade)
print(operational_condition)

# Calculate induction factors for each blade element
print("Calculating induction factors for each blade element...")
blade.compute_induction_factors_blade(operational_condition=operational_condition)

# Run blade element momentum theory
print("Running blade element momentum theory...")
bet = BladeElementTheory(blade=blade)
result = bet.compute_aerodynamic_performance(operational_condition=operational_condition)

# Results _____________________________________________________________

print(f"Total Thrust: {result[0]} N")
print(f"Total Torque: {result[1]} Nm")
print(f"Total Power: {result[2]} W")
print(f"Thrust Coefficient (CT): {result[3]}")
print(f"Power Coefficient (CP): {result[4]}")

# Save results and plots
output_folder = Path(__file__).parent / "outputs" / f"wind_speed_{operational_condition.wind_speed}ms"
output_file = output_folder / "results.txt"

# Create performance analyzer
performance_analyzer = PerformanceAnalyzer(blade=blade, min_wind_speed=min_wind_speed, max_wind_speed=max_wind_speed, num_points=wind_speed_discretisation)

# Save all results and plots
save_results(operational_condition, result, output_file, Data_Source)
save_plots(output_folder, performance_analyzer)

print(f"Results and plots saved in {output_folder}")

blade.plot_blade_shape(10)
plt.show()