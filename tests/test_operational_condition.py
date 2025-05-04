import sys
from pathlib import Path
import pytest
import numpy as np
from unittest.mock import MagicMock

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.OperationalCondition import OperationalCondition
from src.Blade import Blade  # Needed for testing calculate_angular_velocity
from src.OperationalCharacteristics import (
    OperationalCharacteristics,
    OperationalCharacteristic,
)


def test_operational_condition_initialization():
    """Test initialization of an OperationalCondition object with default values."""
    # Test with default values
    condition = OperationalCondition(wind_speed=10.0)

    # Check that initialization worked correctly
    assert condition.wind_speed == 10.0
    assert condition.rho == 1.225  # Default air density
    assert condition.num_blades == 3  # Default number of blades
    assert condition.rpm is None  # Should be None until calculated
    assert condition.omega is None  # Should be None until calculated

    # Test with custom values
    condition = OperationalCondition(wind_speed=15.0, rho=1.1, num_blades=2)

    # Check that initialization with custom values worked correctly
    assert condition.wind_speed == 15.0
    assert condition.rho == 1.1
    assert condition.num_blades == 2
    assert condition.rpm is None
    assert condition.omega is None


def test_operational_condition_repr_and_str():
    """Test the string representation methods of OperationalCondition."""
    condition = OperationalCondition(wind_speed=12.0, rho=1.2, num_blades=3)

    # Test __repr__ method
    repr_str = repr(condition)
    assert "OperationalCondition" in repr_str
    assert "wind_speed=12.0" in repr_str
    assert "rho=1.2" in repr_str
    assert "num_blades=3" in repr_str

    # Test __str__ method
    str_output = str(condition)
    assert "Operational Condition:" in str_output
    assert "Wind Speed: 12.0 m/s" in str_output
    assert "Air Density: 1.2 kg/m^3" in str_output
    assert "Number of Blades: 3" in str_output

    # Test __str__ with rpm and omega set
    condition.rpm = 10.5
    condition.omega = 1.1
    str_with_rpm_omega = str(condition)
    assert "RPM: 10.5" in str_with_rpm_omega
    assert "Angular Velocity: 1.1 rad/s" in str_with_rpm_omega


def test_calculate_angular_velocity():
    """Test the calculation of angular velocity from rpm."""
    # Create a mock blade with operational characteristics
    mock_blade = MagicMock(spec=Blade)
    mock_op_chars = OperationalCharacteristics(
        characteristics=[
            OperationalCharacteristic(
                wind_speed=5.0,
                pitch=0.0,
                rpm=6.0,
                aero_power=1000,
                aero_thrust=2000,
            ),
            OperationalCharacteristic(
                wind_speed=10.0,
                pitch=2.0,
                rpm=8.0,
                aero_power=1500,
                aero_thrust=2500,
            ),
            OperationalCharacteristic(
                wind_speed=15.0,
                pitch=4.0,
                rpm=10.0,
                aero_power=2000,
                aero_thrust=3000,
            ),
        ]
    )
    mock_blade.operational_characteristics = mock_op_chars

    # Create an OperationalCondition with a wind speed that matches one of the characteristics
    condition = OperationalCondition(wind_speed=10.0)
    result = condition.calculate_angular_velocity(mock_blade)

    # Check that rpm was calculated correctly (should be 8.0 for wind_speed=10.0)
    assert condition.rpm == 8.0
    assert result is condition  # Should return self for method chaining

    # Check that omega was calculated correctly (rpm to rad/s conversion)
    expected_omega = 8.0 * 2 * np.pi / 60
    assert condition.omega == pytest.approx(expected_omega)

    # Test interpolation for wind speed between characteristic points
    condition = OperationalCondition(wind_speed=7.5)
    condition.calculate_angular_velocity(mock_blade)

    # For wind_speed=7.5, rpm should be interpolated between 6.0 (at 5.0 m/s) and 8.0 (at 10.0 m/s)
    expected_rpm = 7.0  # Linear interpolation: 6.0 + (7.5-5.0)/(10.0-5.0) * (8.0-6.0)
    assert condition.rpm == pytest.approx(expected_rpm)
    expected_omega = expected_rpm * 2 * np.pi / 60
    assert condition.omega == pytest.approx(expected_omega)
