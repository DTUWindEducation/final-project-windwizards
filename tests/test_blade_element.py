import sys
from pathlib import Path
import pytest
import numpy as np

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.OperationalCondition import OperationalCondition
from src.BladeElement import BladeElement
from src.Airfoil import Airfoil, AeroCoefficients
from src.OperationalCharacteristics import (
    OperationalCharacteristics,
    OperationalCharacteristic,
)


@pytest.fixture
def sample_blade_element():
    """Create a sample BladeElement object for testing."""
    return BladeElement(
        r=5.0,
        twist=10.0,
        chord=0.5,
        airfoil_id=1,
        airfoil=None,  # Assuming airfoil is not needed for this test
    )


@pytest.fixture
def sample_operational_conditions():
    """Create a sample OperationalCondition object for testing."""
    condition = OperationalCondition(wind_speed=10.0, rho=1.225, num_blades=3)
    # Manually set omega since we don't have a Blade object to calculate it
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
        ],
    )


@pytest.fixture
def sample_operational_characteristics():
    """Create sample OperationalCharacteristics for testing."""
    return OperationalCharacteristics(
        characteristics=[
            OperationalCharacteristic(
                wind_speed=8.0,
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
                wind_speed=12.0,
                pitch=4.0,
                rpm=10.0,
                aero_power=2000,
                aero_thrust=3000,
            ),
        ]
    )


def test_blade_element_initialization(sample_blade_element):
    """Test initialization of a BladeElement object."""
    assert sample_blade_element.r == 5.0
    assert sample_blade_element.twist == 10.0
    assert sample_blade_element.chord == 0.5
    assert sample_blade_element.airfoil_id == 1
    assert sample_blade_element.airfoil is None
    assert sample_blade_element.a is None
    assert sample_blade_element.a_prime is None
    assert sample_blade_element.Cn is None
    assert sample_blade_element.Ct is None
    assert sample_blade_element.cl is None
    assert sample_blade_element.cd is None
    assert sample_blade_element.alpha is None
    assert sample_blade_element.phi is None
    assert sample_blade_element.dr is None
    assert sample_blade_element.dT is None
    assert sample_blade_element.dM is None
    assert sample_blade_element.L is None
    assert sample_blade_element.D is None
    assert sample_blade_element.Fn is None
    assert sample_blade_element.Ft is None


def test_blade_element_calculate_solidity(
    sample_blade_element, sample_operational_conditions
):
    """Test calculation of solidity."""
    # Set the radius to a non-zero value to avoid division by zero
    sample_blade_element.r = 5.0
    sample_blade_element.calculate_solidity(sample_operational_conditions)
    assert (
        sample_blade_element.solidity == 0.047746482927568605
    )  # Assuming a known value for this test


def test_compute_element_induction_factors(sample_blade_element):
    """Test computation of induction factors."""
    # Set up parameters for the test
    a = 0.1
    a_prime = 0.1
    wind_speed = 10.0
    omega = 2.0
    r = 5.0
    phi = np.radians(30.0)  # Convert to radians
    Cn = 1.0
    Ct = 0.5
    sample_blade_element.solidity = 0.2  # Set a known solidity for the test

    # Call the method to compute induction factors
    a_result, a_prime_result = sample_blade_element.compute_element_induction_factors(
        a, a_prime, wind_speed, omega, r, phi, Cn, Ct
    )

    # Assert that the computed values are reasonable
    assert a_result is not None
    assert a_prime_result is not None
    # Check that the method actually does something
    assert a_result != a
    assert a_prime_result != a_prime


def test_compute_induction_factors(
    sample_blade_element,
    sample_airfoil,
    sample_operational_characteristics,
    sample_operational_conditions,
):
    """Test computation of induction factors for a blade element with full setup."""
    # Set up the blade element with an airfoil
    sample_blade_element.airfoil = sample_airfoil
    sample_blade_element.solidity = 0.2  # Set solidity

    # Call the compute_induction_factors method
    a_guess = 0.1
    a_prime_guess = 0.05

    # Run the method being tested
    a, a_prime, alpha, cl, cd, phi, Cn, Ct = (
        sample_blade_element.compute_induction_factors(
            a_guess=a_guess,
            a_prime_guess=a_prime_guess,
            operational_characteristics=sample_operational_characteristics,
            operational_condition=sample_operational_conditions,
        )
    )

    # Check that values were computed and stored in the blade element
    assert sample_blade_element.a is not None
    assert sample_blade_element.a_prime is not None
    assert sample_blade_element.alpha is not None
    assert sample_blade_element.cl is not None
    assert sample_blade_element.cd is not None
    assert sample_blade_element.phi is not None
    assert sample_blade_element.Cn is not None
    assert sample_blade_element.Ct is not None

    # Verify returned values match the stored values
    assert a == sample_blade_element.a
    assert a_prime == sample_blade_element.a_prime
    assert alpha == sample_blade_element.alpha
    assert cl == sample_blade_element.cl
    assert cd == sample_blade_element.cd
    assert phi == sample_blade_element.phi
    assert Cn == sample_blade_element.Cn
    assert Ct == sample_blade_element.Ct

    # Check that reasonable values were computed
    assert -0.5 <= a <= 0.5, f"Axial induction factor a={a} outside expected range"
    assert (
        -0.5 <= a_prime <= 0.5
    ), f"Tangential induction factor a_prime={a_prime} outside expected range"
    assert (
        -np.pi / 2 <= alpha <= np.pi / 2
    ), f"Angle of attack alpha={alpha} outside expected range"
    assert 0 <= cl <= 2.0, f"Lift coefficient cl={cl} outside expected range"
    assert 0 <= cd <= 0.1, f"Drag coefficient cd={cd} outside expected range"
    assert 0 <= phi <= np.pi / 2, f"Flow angle phi={phi} outside expected range"
    assert -2.0 <= Cn <= 2.0, f"Normal force coefficient Cn={Cn} outside expected range"
    assert (
        -2.0 <= Ct <= 2.0
    ), f"Tangential force coefficient Ct={Ct} outside expected range"
