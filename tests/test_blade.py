import sys
from pathlib import Path
import pytest
import numpy as np
import tempfile
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.axes
from unittest.mock import MagicMock, patch

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.Blade import Blade
from src.BladeElement import BladeElement
from src.Airfoil import Airfoil, AeroCoefficients
from src.OperationalCondition import OperationalCondition
from src.OperationalCharacteristics import OperationalCharacteristics, OperationalCharacteristic

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
def sample_blade(sample_blade_elements, sample_operational_characteristics):
    """Create a sample Blade object for testing."""
    return Blade(elements=sample_blade_elements, operational_characteristics=sample_operational_characteristics)

@pytest.fixture
def sample_blade_with_airfoils(sample_blade_elements, sample_operational_characteristics, sample_airfoil):
    """Create a sample Blade object with airfoils assigned for testing."""
    for element in sample_blade_elements:
        element.airfoil = sample_airfoil
    return Blade(elements=sample_blade_elements, operational_characteristics=sample_operational_characteristics)

def test_blade_initialization(sample_blade_elements, sample_operational_characteristics):
    """Test initialization of a Blade object."""
    blade = Blade(elements=sample_blade_elements, operational_characteristics=sample_operational_characteristics)
    
    assert blade.elements == sample_blade_elements
    assert blade.R is None
    assert blade.operational_characteristics == sample_operational_characteristics

def test_load_from_file():
    """Test loading blade data from a file."""
    # Create a temporary file with sample blade data
    # Format matches expected: r, x, y, z, twist, chord, airfoil_id
    temp_file_content = """
    ! Sample blade data
    ! r x y z twist chord airfoil_id
    2.0 0.0 0.0 0.0 15.0 0.8 1
    4.0 0.0 0.0 0.0 10.0 0.6 1
    6.0 0.0 0.0 0.0 5.0 0.4 1
    """
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write(temp_file_content)
        temp_file_path = temp_file.name
    
    # Create a sample airfoil map
    airfoil = Airfoil(
        name="TestFoil",
        reynolds=1e6,
        control=1,
        incl_ua_data=True,
        ref_coord=(0.25, 0.0),
        shape_coords=[(0.0, 0.0), (0.5, 0.1), (1.0, 0.0)],
        aero_data=[AeroCoefficients(alpha=0, cl=0.5, cd=0.01, cm=0.02)]
    )
    airfoil_map = {0: airfoil}
    
    # Test loading from file
    blade = Blade()
    blade.load_from_file(Path(temp_file_path), airfoil_map)
    
    # Delete temporary file
    Path(temp_file_path).unlink()
    
    # Check that elements were loaded
    assert len(blade.elements) > 0
    # Check properties of loaded elements
    for element in blade.elements:
        assert isinstance(element, BladeElement)
        assert element.airfoil is airfoil

def test_calculate_element_discretization_lengths(sample_blade):
    """Test calculation of discretization lengths."""
    blade = sample_blade
    blade.calculate_element_discretization_lengths()
    
    # Check that dr values are assigned
    for element in blade.elements:
        assert element.dr is not None
    
    # Check specific dr values based on element spacing
    assert blade.elements[0].dr == (blade.elements[1].r - blade.elements[0].r) / 2
    assert blade.elements[1].dr == (blade.elements[2].r - blade.elements[0].r) / 2
    assert blade.elements[2].dr == (blade.elements[2].r - blade.elements[1].r) / 2

def test_calculate_element_discretization_lengths_empty_blade():
    """Test calculation of discretization lengths with an empty blade."""
    blade = Blade()
    with pytest.raises(ValueError):
        blade.calculate_element_discretization_lengths()

def test_compute_induction_factors_blade(sample_blade_with_airfoils, sample_operational_condition):
    """Test computation of induction factors for all blade elements."""
    blade = sample_blade_with_airfoils
    
    # Compute induction factors
    updated_elements = blade.compute_induction_factors_blade(
        a_guess=0.1,
        a_prime_guess=0.05,
        max_iterations=50,
        tolerance=1e-4,
        operational_condition=sample_operational_condition
    )
    
    # Check that the method returns the elements list
    assert updated_elements == blade.elements
    
    # Check that tip radius (R) is set
    assert blade.R == 6.0  # Max radius from our sample elements
    
    # Check that induction factors and other properties are computed for each element
    for element in blade.elements:
        assert element.dr is not None
        assert element.solidity is not None
        assert hasattr(element, 'a')
        assert hasattr(element, 'a_prime')
        assert hasattr(element, 'phi')

def test_load_from_file_with_invalid_data():
    """Test loading blade data from a file with invalid data."""
    # Create a temporary file with invalid blade data
    temp_file_content = """
    ! Sample blade data with errors
    ! r x y z twist chord airfoil_id
    2.0 0.0 0.0 0.0 fifteen 0.8 1
    4.0 0.0 0.0 0.0 10.0 0.6 one
    not_a_number 0.0 0.0 0.0 5.0 0.4 1
    """
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write(temp_file_content)
        temp_file_path = temp_file.name
    
    # Create a sample airfoil map
    airfoil = Airfoil(
        name="TestFoil",
        reynolds=1e6,
        control=1,
        incl_ua_data=True,
        ref_coord=(0.25, 0.0),
        shape_coords=[(0.0, 0.0), (0.5, 0.1), (1.0, 0.0)],
        aero_data=[AeroCoefficients(alpha=0, cl=0.5, cd=0.01, cm=0.02)]
    )
    airfoil_map = {0: airfoil}
    
    # Test loading from file with invalid data
    blade = Blade()
    blade.load_from_file(Path(temp_file_path), airfoil_map)
    
    # Delete temporary file
    Path(temp_file_path).unlink()
    
    # Check that no elements were loaded (all lines have errors)
    assert len(blade.elements) == 0

def test_load_from_file_with_insufficient_columns():
    """Test loading blade data from a file with insufficient columns."""
    # Create a temporary file with insufficient columns
    temp_file_content = """
    ! Sample blade data with insufficient columns
    ! r x y z twist chord
    2.0 0.0 0.0 0.0 15.0 0.8
    4.0 0.0 0.0 0.0 10.0 0.6
    """
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write(temp_file_content)
        temp_file_path = temp_file.name
    
    # Test loading from file with insufficient columns
    blade = Blade()
    blade.load_from_file(Path(temp_file_path), None)
    
    # Delete temporary file
    Path(temp_file_path).unlink()
    
    # Check that no elements were loaded
    assert len(blade.elements) == 0

def test_plot_blade_shape(sample_blade_with_airfoils):
    """Test plotting blade shape with proper mocking of matplotlib."""
    # Setup - prepare a blade with airfoils that have shape coordinates
    blade = sample_blade_with_airfoils
    blade.R = 6.0  # Set tip radius
    
    # Mock matplotlib methods to avoid display issues
    with patch('matplotlib.pyplot.figure', return_value=MagicMock()) as mock_figure, \
         patch('matplotlib.pyplot.show') as mock_show, \
         patch('matplotlib.pyplot.subplot', return_value=MagicMock()) as mock_subplot:
        
        # Call the method being tested
        blade.plot_blade_shape(scale_factor=5)
        
        # Verify the method calls - simply check that these functions were called at least once
        assert mock_figure.called
        assert mock_show.called
        
        # We don't verify subplot calls as they're made through add_subplot in the implementation

def test_plot_blade_shape_with_no_airfoil(sample_blade):
    """Test plotting blade shape with elements that don't have airfoils."""
    blade = sample_blade
    blade.R = 6.0  # Set tip radius
    
    # Mock matplotlib methods
    with patch('matplotlib.pyplot.figure', return_value=MagicMock()) as mock_figure, \
         patch('matplotlib.pyplot.show') as mock_show:
        
        # Call the method - this should not plot any airfoils but still work
        blade.plot_blade_shape()
        
        # Verify basic calls were made - check that functions were called at least once
        assert mock_figure.called
        assert mock_show.called

def test_plot_blade_shape_with_empty_blade():
    """Test plotting blade shape with an empty blade."""
    blade = Blade()
    
    # Mock matplotlib methods
    with patch('matplotlib.pyplot.figure', return_value=MagicMock()) as mock_figure, \
         patch('matplotlib.pyplot.show') as mock_show:
        
        # Call the method - should handle empty blade gracefully
        blade.plot_blade_shape()
        
        # Verify basic calls were made - check that functions were called at least once
        assert mock_figure.called
        assert mock_show.called

def test_repr_and_str_methods(sample_blade):
    """Test the __repr__ and __str__ methods of the Blade class."""
    blade = sample_blade
    blade.R = 6.0  # Set tip radius
    
    # Test __repr__ method
    repr_string = repr(blade)
    assert "Blade with" in repr_string
    assert str(len(blade.elements)) in repr_string
    
    # Test __str__ method
    str_string = str(blade)
    assert "Blade:" in str_string
    assert "Number of Elements: " + str(len(blade.elements)) in str_string
    assert "Tip Radius: " + str(blade.R) in str_string

def test_empty_blade_str_repr():
    """Test string representation of an empty blade."""
    blade = Blade()
    
    # Test __repr__ method for empty blade
    repr_string = repr(blade)
    assert "Blade with 0 elements" in repr_string
    
    # Test __str__ method for empty blade
    str_string = str(blade)
    assert "Number of Elements: 0" in str_string
    assert "Tip Radius: None" in str_string