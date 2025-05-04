from src.Airfoil import Airfoil, AeroCoefficients, plot_airfoil_shapes
import sys
from pathlib import Path
import pytest

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


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
        ],
    )


def test_airfoil_initialization(sample_airfoil):
    """Test initialization of an Airfoil object."""
    assert sample_airfoil.name == "TestFoil"
    assert sample_airfoil.reynolds == 1e6
    assert sample_airfoil.control == 1
    assert sample_airfoil.incl_ua_data is True


def test_airfoil_repr(sample_airfoil):
    """Test the __repr__ output of the Airfoil object."""
    repr_str = repr(sample_airfoil)
    assert "TestFoil" in repr_str
    assert "reynolds=1000000.0" in repr_str
    assert "num_shape_coords=3" in repr_str
    assert "num_aero_data=2" in repr_str


def test_plot_airfoil_shapes(sample_airfoil):
    """Test that plot_airfoil_shapes runs without errors."""
    plot_airfoil_shapes(
        [sample_airfoil],
        [0])  # Only checking that no exception occurs


def test_load_from_file(tmp_path):
    """Test load_from_file with a small dummy file."""
    dummy_file = tmp_path / "AF01.txt"
    dummy_file.write_text(
        "! x-y coordinate of airfoil reference\n"
        "\n"
        "0.25 0.0\n"
        "3 NumCoords\n"
        "! coordinates of airfoil shape\n"
        "\n"
        "0.0 0.0\n"
        "0.5 0.1\n"
        "1.0 0.0\n"
    )

    airfoil = Airfoil(name="", reynolds=0, control=0, incl_ua_data=False)
    airfoil.load_from_file(dummy_file)

    assert airfoil.name == "Airfoil 01"
    assert airfoil.ref_coord == (0.25, 0.0)
    assert len(airfoil.shape_coords) == 3


def test_load_from_polar_and_coords(tmp_path):
    """Test load_from_polar_and_coords with dummy coordinate and polar files."""
    # Create dummy coordinate file
    coord_file = tmp_path / "AF02.txt"
    coord_file.write_text(
        "! x-y coordinate of airfoil reference\n"
        "\n"
        "0.3 0.0\n"
        "2 NumCoords\n"
        "! coordinates of airfoil shape\n"
        "\n"
        "0.0 0.0\n"
        "1.0 0.0\n"
    )

    # Create dummy polar file
    polar_file = tmp_path / "polar.txt"
    polar_file.write_text(
        "6.0 ! Reynolds number in millions\n"
        "2 Ctrl\n"
        "true InclUAdata\n"
        "NumAlf\n"
        "0 0.5 0.01 0.02\n"
        "5 0.7 0.02 0.03\n"
    )

    airfoil = Airfoil(name="", reynolds=0, control=0, incl_ua_data=False)
    airfoil.load_from_polar_and_coords(coord_file, polar_file)

    assert airfoil.reynolds == 6_000_000
    assert airfoil.control == 2
    assert airfoil.incl_ua_data is True
    assert len(airfoil.aero_data) == 2
    assert airfoil.aero_data[0].alpha == 0
    assert airfoil.aero_data[1].cl == 0.7
