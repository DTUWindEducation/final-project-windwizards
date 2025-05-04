import sys
from pathlib import Path
import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch
import matplotlib.pyplot as plt

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import save_results, save_plots
from src.OperationalCondition import OperationalCondition
from src.PerformanceAnalyzer import PerformanceAnalyzer


def test_save_results():
    """Test the save_results function that writes simulation results to a file."""
    # Create mock operational condition
    operational_condition = MagicMock()
    operational_condition.wind_speed = 10.0
    operational_condition.rho = 1.225
    operational_condition.num_blades = 3

    # Create sample results
    results = (
        1000.0,
        2000.0,
        50000.0,
        0.75,
        0.45,
    )  # thrust, torque, power, ct, cp

    # Use a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create output file path
        output_file = Path(temp_dir) / "test_results.txt"

        # Call the function being tested
        save_results(operational_condition, results, output_file, "Test-Source")

        # Check if the file was created
        assert output_file.exists(), "Results file was not created"

        # Read the file contents
        content = output_file.read_text()

        # Check if the content includes expected values
        assert "=== Wind Turbine Simulation Results ===" in content
        assert "Data Source: Test-Source" in content
        assert "Wind Speed: 10.00 m/s" in content
        assert "Air Density: 1.23 kg/m^3" in content
        assert "Number of Blades: 3" in content
        assert "Total Thrust: 1000.00 N" in content
        assert "Total Torque: 2000.00 Nm" in content
        assert "Total Power: 50000.00 W" in content
        assert "Thrust Coefficient (CT): 0.7500" in content
        assert "Power Coefficient (CP): 0.4500" in content


@patch("matplotlib.pyplot.savefig")
@patch("matplotlib.pyplot.close")
def test_save_plots(mock_close, mock_savefig):
    """Test the save_plots function that creates and saves plots."""
    # Create a mock performance analyzer
    performance_analyzer = MagicMock(spec=PerformanceAnalyzer)

    # Use a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        output_folder = Path(temp_dir)

        # Call the function being tested
        save_plots(output_folder, performance_analyzer)

        # Check if the method calls the expected methods on performance_analyzer
        assert performance_analyzer.plot_power_curve.call_count == 1
        assert performance_analyzer.plot_thrust_curve.call_count == 1
        assert performance_analyzer.plot_torque_curve.call_count == 1

        # Check that savefig was called 3 times (once for each plot)
        assert mock_savefig.call_count == 3

        # Check that close was called 3 times (once for each plot)
        assert mock_close.call_count == 3

        # Check the savefig calls contain the expected filenames
        expected_filenames = [
            "power_curve.png",
            "thrust_curve.png",
            "torque_curve.png",
        ]

        for i, call_args in enumerate(mock_savefig.call_args_list):
            # Extract the filename from the Path object
            saved_path = call_args[0][0]
            filename = Path(saved_path).name
            assert (
                filename == expected_filenames[i]
            ), f"Expected {expected_filenames[i]} but got {filename}"
