import sys
from pathlib import Path
import pytest
import numpy as np
from unittest.mock import MagicMock, patch

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.Blade import Blade
from src.BladeElement import BladeElement
from src.Airfoil import Airfoil, AeroCoefficients
from src.OperationalCondition import OperationalCondition
from src.OperationalCharacteristics import OperationalCharacteristics, OperationalCharacteristic
from src.BladeElementTheory import BladeElementTheory

@pytest.fixture
def sample_blade_elements():
    """Create a list of sample BladeElement objects for testing."""
    elements = [
        BladeElement(r=2.0, twist=15.0, chord=0.8, airfoil_id=0),
        BladeElement(r=4.0, twist=10.0, chord=0.6, airfoil_id=0),
        BladeElement(r=6.0, twist=5.0, chord=0.4, airfoil_id=0)
    ]
    return elements

@pytest.fixture
def sample_operational_characteristics():
    """Create sample OperationalCharacteristics for testing."""
    return OperationalCharacteristics(
        characteristics=[
            OperationalCharacteristic(wind_speed=8.0, pitch=0.0, rpm=6.0, aero_power=1000, aero_thrust=2000),
            OperationalCharacteristic(wind_speed=10.0, pitch=2.0, rpm=8.0, aero_power=1500, aero_thrust=2500),
            OperationalCharacteristic(wind_speed=12.0, pitch=4.0, rpm=10.0, aero_power=2000, aero_thrust=3000),
        ]
    )

@pytest.fixture
def sample_operational_condition():
    """Create a sample OperationalCondition object for testing."""
    condition = OperationalCondition(
        wind_speed=10.0,
        rho=1.225,
        num_blades=3
    )
    condition.omega = 0.8  # Set a reasonable value in rad/s (~ 7.6 RPM)
    return condition

@pytest.fixture
def sample_airfoil():
    """Create a sample Airfoil object for testing."""
    return Airfoil(
        name="TestFoil",
        reynolds=1e6,
        control=1,
        incl_ua_data=True,
        ref_coord=(0.25, 0.0),
        shape_coords=[(0.0, 0.0), (0.5, 0.1), (1.0, 0.0)],
        aero_data=[
            AeroCoefficients(alpha=0, cl=0.5, cd=0.01, cm=0.02),
            AeroCoefficients(alpha=5, cl=0.7, cd=0.02, cm=0.03),
            AeroCoefficients(alpha=10, cl=0.9, cd=0.03, cm=0.04),
            AeroCoefficients(alpha=15, cl=1.1, cd=0.04, cm=0.05),
        ]
    )

@pytest.fixture
def prepared_blade_elements(sample_blade_elements, sample_operational_condition, sample_airfoil):
    """Create blade elements with pre-computed aerodynamic properties for testing."""
    elements = sample_blade_elements
    
    # Set airfoil for all elements
    for element in elements:
        element.airfoil = sample_airfoil
        element.dr = 1.0  # Set discretization length
        element.calculate_solidity(operational_conditions=sample_operational_condition)
        
        # Set pre-computed values for aerodynamic calculations
        element.a = 0.3  # Sample axial induction factor
        element.a_prime = 0.1  # Sample tangential induction factor
        element.alpha = np.radians(5.0)  # Sample angle of attack
        element.phi = np.radians(15.0)  # Sample flow angle
        element.cl = 0.7  # Sample lift coefficient
        element.cd = 0.02  # Sample drag coefficient
        element.Cn = element.cl * np.cos(element.phi) + element.cd * np.sin(element.phi)
        element.Ct = element.cl * np.sin(element.phi) - element.cd * np.cos(element.phi)
    
    return elements

@pytest.fixture
def sample_blade(prepared_blade_elements, sample_operational_characteristics):
    """Create a sample Blade object with prepared elements for testing."""
    blade = Blade(elements=prepared_blade_elements, operational_characteristics=sample_operational_characteristics)
    blade.R = 6.0  # Set tip radius
    return blade

@pytest.fixture
def sample_blade_element_theory(sample_blade):
    """Create a sample BladeElementTheory object for testing."""
    return BladeElementTheory(blade=sample_blade)

def test_initialization(sample_blade):
    """Test initialization of BladeElementTheory."""
    bet = BladeElementTheory(blade=sample_blade)
    assert bet.blade == sample_blade

def test_compute_aerodynamic_performance(sample_blade_element_theory, sample_operational_condition):
    """Test the compute_aerodynamic_performance method."""
    # Call the method being tested
    total_thrust, total_torque, total_power, ct, cp = sample_blade_element_theory.compute_aerodynamic_performance(
        operational_condition=sample_operational_condition
    )
    
    # Assert that the results are of the expected types
    assert isinstance(total_thrust, (int, float))
    assert isinstance(total_torque, (int, float))
    assert isinstance(total_power, (int, float))
    assert isinstance(ct, (int, float))
    assert isinstance(cp, (int, float))
    
    # Assert that the results are physically reasonable
    assert total_thrust >= 0, "Thrust should be non-negative"
    assert total_torque >= 0, "Torque should be non-negative for a properly oriented wind turbine"
    assert total_power >= 0, "Power should be non-negative"
    assert 0 <= ct <= 1.0, f"Thrust coefficient (CT={ct}) should be between 0 and 1"
    assert 0 <= cp <= 0.593, f"Power coefficient (CP={cp}) should be between 0 and Betz limit (0.593)"
    
    # Verify that power = torque * omega
    assert abs(total_power - total_torque * sample_operational_condition.omega) < 1e-10, "Power should equal torque times angular velocity"

def test_element_forces_calculation(sample_blade_element_theory, sample_operational_condition):
    """Test that forces are properly calculated and stored in each blade element."""
    # Call the method
    sample_blade_element_theory.compute_aerodynamic_performance(operational_condition=sample_operational_condition)
    
    # Check that forces are calculated for each element
    for element in sample_blade_element_theory.blade.elements:
        assert element.dT is not None, "Element thrust should be calculated"
        assert element.dM is not None, "Element moment should be calculated"
        assert element.L is not None, "Element lift should be calculated"
        assert element.D is not None, "Element drag should be calculated"
        assert element.Fn is not None, "Element normal force should be calculated"
        assert element.Ft is not None, "Element tangential force should be calculated"
        assert element.V_rel is not None, "Element relative velocity should be calculated"
        
        # Verify relations between forces
        assert abs(element.Fn - (element.L * np.cos(element.phi) + element.D * np.sin(element.phi))) < 1e-10, "Normal force calculation error"
        assert abs(element.Ft - (element.L * np.sin(element.phi) - element.D * np.cos(element.phi))) < 1e-10, "Tangential force calculation error"

def test_zero_wind_speed(sample_blade_element_theory):
    """Test performance calculation with zero wind speed."""
    # Create an operational condition with zero wind speed
    zero_wind_condition = OperationalCondition(wind_speed=0.0, rho=1.225, num_blades=3)
    zero_wind_condition.omega = 0.0  # Also zero rotation
    
    # Call the method
    total_thrust, total_torque, total_power, ct, cp = sample_blade_element_theory.compute_aerodynamic_performance(
        operational_condition=zero_wind_condition
    )
    
    # With zero wind speed, all outputs should be zero
    assert total_thrust == 0, "Thrust should be zero with no wind"
    assert total_torque == 0, "Torque should be zero with no wind"
    assert total_power == 0, "Power should be zero with no wind"
    assert ct == 0, "CT should be zero with no wind"
    assert cp == 0, "CP should be zero with no wind"

def test_extreme_conditions(sample_blade_element_theory):
    """Test performance under extreme conditions."""
    # Create an operational condition with very high wind speed
    high_wind_condition = OperationalCondition(wind_speed=50.0, rho=1.225, num_blades=3)
    high_wind_condition.omega = 0.8
    
    # Call the method with high wind speed
    results_high_wind = sample_blade_element_theory.compute_aerodynamic_performance(
        operational_condition=high_wind_condition
    )
    
    # Values should be higher than with normal wind
    normal_wind_condition = OperationalCondition(wind_speed=10.0, rho=1.225, num_blades=3)
    normal_wind_condition.omega = 0.8
    results_normal_wind = sample_blade_element_theory.compute_aerodynamic_performance(
        operational_condition=normal_wind_condition
    )
    
    # Thrust and power should be higher with higher wind speed
    assert results_high_wind[0] > results_normal_wind[0], "Thrust should increase with wind speed"
    assert results_high_wind[2] > results_normal_wind[2], "Power should increase with wind speed"

def test_integration_with_blade_class(sample_blade, sample_operational_condition):
    """Test integration between BladeElementTheory and Blade classes."""
    # Setup
    bet = BladeElementTheory(blade=sample_blade)
    
    # Perform calculation
    total_thrust, total_torque, total_power, ct, cp = bet.compute_aerodynamic_performance(
        operational_condition=sample_operational_condition
    )
    
    # Verify results
    assert total_thrust is not None
    assert total_torque is not None
    assert total_power is not None
    assert ct is not None
    assert cp is not None
    
    # Verify that element properties were updated
    for element in sample_blade.elements:
        assert element.dT is not None
        assert element.dM is not None