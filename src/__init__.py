""" Source code for small functions used in the project. """

import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def save_results(operational_condition, results, output_file, input_folder):
    """
    Save simulation results to a text file.
    
    Parameters:
        operational_condition (OperationalCondition): The operational condition object
        results (tuple): Tuple containing (thrust, torque, power, ct, cp)
        output_file (Path): Path to save the results
    """
    thrust, torque, power, ct, cp = results
    
    output_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    with open(output_file, 'w') as f:

        f.write("=== Wind Turbine Simulation Results ===\n")
        f.write(f"\nData Source: {input_folder}\n")
        f.write("\n=== Operational Conditions ===\n")
        f.write(f"Wind Speed: {operational_condition.wind_speed:.2f} m/s\n")
        f.write(f"Air Density: {operational_condition.rho:.2f} kg/m^3\n")
        f.write(f"Number of Blades: {operational_condition.num_blades}\n")
        f.write("\n=== Results ===\n")
        f.write(f"Total Thrust: {thrust:.2f} N\n")
        f.write(f"Total Torque: {torque:.2f} Nm\n")
        f.write(f"Total Power: {power:.2f} W\n")
        f.write(f"Thrust Coefficient (CT): {ct:.4f}\n")
        f.write(f"Power Coefficient (CP): {cp:.4f}\n")

def save_plots(output_folder, performance_analyzer):
    """
    Save all plots to the output folder.
    
    Parameters:
        output_folder (Path): Directory to save the plots
        blade (Blade): Blade object
        performance_analyzer (PerformanceAnalyzer): Performance analyzer object
    """
    # Create output directory if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)

    # Save performance curves
    power_curve_plot = output_folder / "power_curve.png"
    performance_analyzer.plot_power_curve()
    plt.savefig(power_curve_plot)
    plt.close()

    thrust_curve_plot = output_folder / "thrust_curve.png"
    performance_analyzer.plot_thrust_curve()
    plt.savefig(thrust_curve_plot)
    plt.close()

    torque_curve_plot = output_folder / "torque_curve.png"
    performance_analyzer.plot_torque_curve()
    plt.savefig(torque_curve_plot)
    plt.close()