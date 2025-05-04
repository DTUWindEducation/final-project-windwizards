"""Main script for wind turbine blade analysis."""

# Standard library imports
from pathlib import Path

# Third-party imports
import matplotlib.pyplot as plt

# Local imports
from src.Airfoil import Airfoil, plot_airfoil_shapes
from src.Blade import Blade
from src.OperationalCharacteristics import (
    OperationalCharacteristics,
)
from src.OperationalCondition import OperationalCondition
from src.BladeElementTheory import BladeElementTheory
from src.PerformanceAnalyzer import PerformanceAnalyzer
from src import save_results, save_plots


# Input _______________________________________________________________________

# Define operational conditions
wind_speed = 10.0  # Wind speed in m/s
rho = 1.225  # Air density in kg/m^3 (standard value at sea level)
num_blades = 3  # Number of blades

# Define Wind Conditions for performance analysis
min_wind_speed = 0  # Minimum wind speed for performance analysis
max_wind_speed = 25  # Maximum wind speed for performance analysis
wind_speed_discretisation = 100  # Number of points for wind speed discretization

# Define calculation parameters for induction factors
a_guess = 0.0  # Initial guess for axial induction factor
a_prime_guess = 0.0  # Initial guess for tangential induction factor

max_iterations = 100  # Maximum number of iterations for convergence
tolerance = 1e-5  # Tolerance for convergence

# Define radius for which the aerodynamics parameters are calulated
radius = 30.0  # Radius of the rotor in meters

# Define airfoil indices to plot
airfoil_indices = [0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49]

# Define the blade data source
Data_Source = "IEA-15-240-RWT"  # Data source name

# Loading Data ________________________________________________________________

# Set the Data source base path
base_path = Path(__file__).parent / "inputs" / Data_Source

# Load airfoils into a dictionary
print("Loading airfoils...")
airfoil_map = {}

# Iterate through all coordinate files in the Airfoils directory
for coord_file in (
        base_path /
        "Airfoils").glob("IEA-15-240-RWT_AF*_Coords.txt"):
    # Extract the index from the filename
    idx = coord_file.stem.split("_")[-2][2:]
    polar_file = base_path / \
        f"Airfoils/IEA-15-240-RWT_AeroDyn15_Polar_{idx}.dat"

    # Create Airfoil object and load data from the files
    airfoil = Airfoil(name="", reynolds=0.0, control=0, incl_ua_data=False)
    airfoil.load_from_polar_and_coords(coord_file, polar_file)

    # Store the Airfoil in the map
    airfoil_map[int(idx)] = airfoil

print(f"Loaded {len(airfoil_map)} airfoils")

# Load operational conditions
print("Loading operational characteristics...")
opt_file = base_path / "IEA_15MW_RWT_Onshore.opt"
ops = OperationalCharacteristics()
ops.load_from_file(opt_file)
print(f"Loaded {len(ops.characteristics)} operational characteristics")

# Load blade data
print("Loading blade...")
blade_file = base_path / "IEA-15-240-RWT_AeroDyn15_blade.dat"
# Initialize blade with operational characteristics
blade = Blade(operational_characteristics=ops)
blade.load_from_file(file_path=blade_file, airfoil_map=airfoil_map)
print(f"Loaded blade with {len(blade.elements)} elements")
# print(f"Blade characteristic: {blade.operational_characteristics} m")
# ops.plot_characteristics(V_min=0, V_max=30, num_points=100)

# Processing  Data _______________________________________________________

# Create operational condition object
operational_condition = OperationalCondition(
    wind_speed=wind_speed, rho=rho, num_blades=num_blades)
operational_condition.calculate_angular_velocity(blade=blade)
print("-" * 40)
print(operational_condition)

# Calculate induction factors for each blade element
print("Calculating induction factors for each blade element...")
blade.compute_induction_factors_blade(
    operational_condition=operational_condition)

# Run blade element momentum theory
print("Running blade element momentum theory...")
bet = BladeElementTheory(blade=blade)
result = bet.compute_aerodynamic_performance(
    operational_condition=operational_condition)
aerodata_at_radius = bet.compute_induction_factors(
    radius=radius,
    a_guess=a_guess,
    a_prime_guess=a_prime_guess,
    max_iterations=max_iterations,
    tolerance=tolerance,
    operational_characteristics=ops,
    operational_condition=operational_condition,
)

# Calculate aerodynamic performance for the specified wind speed range
performance_analyzer = PerformanceAnalyzer(
    blade=blade, min_wind_speed=1, max_wind_speed=30, num_points=100
)


# Results _____________________________________________________________

# Plot selected airfoil shapes
print("\nPlotting selected airfoil shapes...")
plot_airfoil_shapes(list(airfoil_map.values()), airfoil_indices)

print("Plotting blade shape...")
blade.plot_blade_shape(15)

print("Plotting Power, Thrust, Torque...")
performance_analyzer.plot_power_curve()
performance_analyzer.plot_thrust_curve()
performance_analyzer.plot_torque_curve()

# Print aerodynamic data for the specified radius
print("-" * 40)

print(f"\nAerodynamic data at radius {radius} m:")
print(f"Radius: {aerodata_at_radius['radius']:.2f} m")
print(f"Axial induction factor (a): {aerodata_at_radius['a']:.4f}")
print(f"Tangential induction factor (a'): {aerodata_at_radius['a_prime']:.4f}")
print(f"Angle of attack (alpha): {aerodata_at_radius['alpha']:.2f} degrees")
print(f"Lift coefficient (Cl): {aerodata_at_radius['cl']:.4f}")
print(f"Drag coefficient (Cd): {aerodata_at_radius['cd']:.4f}")
print(f"Flow angle (phi): {aerodata_at_radius['phi']:.2f} degrees")
print(f"Normal force coefficient (Cn): {aerodata_at_radius['Cn']:.4f}")
print(f"Thrust force coefficient (Ct): {aerodata_at_radius['Ct']:.4f}")

print("-" * 40)

print("Aerodynamic performance results:")
print(f"Total Thrust: {result[0]:.2f} N")
print(f"Total Torque: {result[1]:.2f} Nm")
print(f"Total Power: {result[2]:.2f} W")
print(f"Thrust Coefficient (CT): {result[3]:.2f}")
print(f"Power Coefficient (CP): {result[4]:.2f}")

print("-" * 40)

# Save results and plots
output_folder = (
    Path(__file__).parent /
    "outputs" /
    f"wind_speed_{
        operational_condition.wind_speed}ms")
output_file = output_folder / "results.txt"

# Save all results and plots
save_results(operational_condition, result, output_file, Data_Source)
save_plots(output_folder, performance_analyzer)

print(f"Results and plots saved in {output_folder}")
print("-" * 40)

plt.show()
