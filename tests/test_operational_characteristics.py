import sys
from pathlib import Path
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.OperationalCharacteristics import OperationalCharacteristic, OperationalCharacteristics


def test_operational_characteristic_init():
    """Test initialization of an OperationalCharacteristic object."""
    # Test with default rho value
    characteristic = OperationalCharacteristic(
        wind_speed=10.0,
        pitch=2.0,
        rpm=8.0,
        aero_power=1500,
        aero_thrust=2500
    )
    
    # Check that initialization worked correctly
    assert characteristic.wind_speed == 10.0
    assert characteristic.pitch == 2.0
    assert characteristic.rpm == 8.0
    assert characteristic.aero_power == 1500
    assert characteristic.aero_thrust == 2500
    assert characteristic.rho == 1.225  # Default air density
    
    # Verify omega calculation (rpm to rad/s conversion)
    expected_omega = 8.0 * 2 * np.pi / 60
    assert characteristic.omega == pytest.approx(expected_omega)
    
    # Test with custom rho value
    characteristic = OperationalCharacteristic(
        wind_speed=15.0,
        pitch=4.0,
        rpm=10.0,
        aero_power=2000,
        aero_thrust=3000,
        rho=1.1
    )
    
    # Check that initialization with custom values worked correctly
    assert characteristic.wind_speed == 15.0
    assert characteristic.pitch == 4.0
    assert characteristic.rpm == 10.0
    assert characteristic.aero_power == 2000
    assert characteristic.aero_thrust == 3000
    assert characteristic.rho == 1.1
    
    # Verify omega calculation for the second case
    expected_omega = 10.0 * 2 * np.pi / 60
    assert characteristic.omega == pytest.approx(expected_omega)


def test_operational_characteristic_repr():
    """Test the string representation (__repr__) of OperationalCharacteristic."""
    characteristic = OperationalCharacteristic(
        wind_speed=12.0, 
        pitch=3.0, 
        rpm=9.0, 
        aero_power=1800, 
        aero_thrust=2800
    )
    
    # Test __repr__ method
    repr_str = repr(characteristic)
    assert "OperationalCharacteristic" in repr_str
    assert "wind_speed=12.0" in repr_str
    assert "pitch=3.0" in repr_str
    assert "rpm=9.0" in repr_str
    assert "aero_power=1800" in repr_str
    assert "aero_thrust=2800" in repr_str


def test_operational_characteristics_init():
    """Test initialization of an OperationalCharacteristics object."""
    # Test with empty list
    characteristics = OperationalCharacteristics()
    assert characteristics.characteristics == []
    
    # Test with a list of OperationalCharacteristic objects
    char1 = OperationalCharacteristic(wind_speed=10.0, pitch=2.0, rpm=8.0, aero_power=1500, aero_thrust=2500)
    char2 = OperationalCharacteristic(wind_speed=15.0, pitch=4.0, rpm=10.0, aero_power=2000, aero_thrust=3000)
    
    characteristics = OperationalCharacteristics([char1, char2])
    assert len(characteristics.characteristics) == 2
    assert characteristics.characteristics[0] is char1
    assert characteristics.characteristics[1] is char2


def test_load_from_file():
    """Test loading operational characteristics from a file."""
    # Mock file content
    file_content = """
    # This is a comment
    ------------------
    5.0 1.0 6.0 1000 2000
    10.0 2.0 8.0 1500 2500
    15.0 3.0 10.0 2000 3000
    invalid line
    20.0 4.0 garbage 2500 3500
    25.0 5.0 12.0 3000 4000
    """
    
    # Create a mock Path object
    mock_path = MagicMock()
    mock_path.read_text.return_value = file_content
    
    # Create an OperationalCharacteristics instance and load data
    characteristics = OperationalCharacteristics()
    characteristics.load_from_file(mock_path)
    
    # Check that valid lines were parsed correctly
    # Only 3 valid lines in our test data because the line with "garbage" is invalid
    assert len(characteristics.characteristics) == 4
    
    # Check first valid entry
    assert characteristics.characteristics[0].wind_speed == 5.0
    assert characteristics.characteristics[0].pitch == 1.0
    assert characteristics.characteristics[0].rpm == 6.0
    assert characteristics.characteristics[0].aero_power == 1000
    assert characteristics.characteristics[0].aero_thrust == 2000
    
    # Check second valid entry
    assert characteristics.characteristics[1].wind_speed == 10.0
    assert characteristics.characteristics[1].pitch == 2.0
    assert characteristics.characteristics[1].rpm == 8.0
    assert characteristics.characteristics[1].aero_power == 1500
    assert characteristics.characteristics[1].aero_thrust == 2500
    
    # Check third valid entry
    assert characteristics.characteristics[2].wind_speed == 15.0
    assert characteristics.characteristics[2].pitch == 3.0
    assert characteristics.characteristics[2].rpm == 10.0
    assert characteristics.characteristics[2].aero_power == 2000
    assert characteristics.characteristics[2].aero_thrust == 3000


def test_operational_characteristics_repr():
    """Test the string representation of OperationalCharacteristics."""
    # Test with empty characteristics
    characteristics = OperationalCharacteristics()
    assert repr(characteristics) == "OperationalCharacteristics(num_conditions=0)."
    
    # Test with some characteristics
    char1 = OperationalCharacteristic(wind_speed=10.0, pitch=2.0, rpm=8.0, aero_power=1500, aero_thrust=2500)
    char2 = OperationalCharacteristic(wind_speed=15.0, pitch=4.0, rpm=10.0, aero_power=2000, aero_thrust=3000)
    
    characteristics = OperationalCharacteristics([char1, char2])
    assert repr(characteristics) == "OperationalCharacteristics(num_conditions=2)."


@patch('matplotlib.pyplot.figure')
@patch('matplotlib.pyplot.plot')
@patch('matplotlib.pyplot.xlabel')
@patch('matplotlib.pyplot.ylabel')
@patch('matplotlib.pyplot.title')
@patch('matplotlib.pyplot.legend')
@patch('matplotlib.pyplot.grid')
@patch('matplotlib.pyplot.show')
def test_plot_characteristics(mock_show, mock_grid, mock_legend, mock_title, 
                             mock_ylabel, mock_xlabel, mock_plot, mock_figure):
    """Test plotting of operational characteristics."""
    # Create test data
    char1 = OperationalCharacteristic(wind_speed=5.0, pitch=1.0, rpm=6.0, aero_power=1000, aero_thrust=2000)
    char2 = OperationalCharacteristic(wind_speed=10.0, pitch=2.0, rpm=8.0, aero_power=1500, aero_thrust=2500)
    char3 = OperationalCharacteristic(wind_speed=15.0, pitch=3.0, rpm=10.0, aero_power=2000, aero_thrust=3000)
    
    characteristics = OperationalCharacteristics([char1, char2, char3])
    
    # Call the plot method
    characteristics.plot_characteristics(V_min=0, V_max=20, num_points=5)
    
    # Check that the figure was created
    mock_figure.assert_called_once()
    
    # Check that plot was called twice (once for pitch, once for omega)
    assert mock_plot.call_count == 2
    
    # Verify that the plot function was called with appropriate data
    # The first call should be for pitch angle
    x_values, y_values = mock_plot.call_args_list[0][0]
    
    # Expected wind speeds: linspace from 0 to 20 with 5 points
    expected_wind_speeds = np.linspace(0, 20, 5)
    np.testing.assert_array_almost_equal(x_values, expected_wind_speeds)
    
    # Check that appropriate labels and titles were set
    mock_xlabel.assert_called_once_with('Wind Speed (m/s)')
    mock_ylabel.assert_called_once_with('Operational Characteristics')
    mock_title.assert_called_once_with('Operational Characteristics vs Wind Speed')
    mock_legend.assert_called_once()
    mock_grid.assert_called_once()
    mock_show.assert_called_once()