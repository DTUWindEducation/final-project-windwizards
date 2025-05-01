import pytest
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import MagicMock, patch

from src.PerformanceAnalyzer import PerformanceAnalyzer
from src.Blade import Blade
from src.BladeElementTheory import BladeElementTheory
from src.OperationalCondition import OperationalCondition


@pytest.fixture
def mock_blade():
    """Create a mock Blade object for testing."""
    blade = MagicMock(spec=Blade)
    # Add any necessary attributes or mock returns here
    return blade


@pytest.fixture
def mock_bet():
    """Create a mock BladeElementTheory object for testing."""
    bet = MagicMock(spec=BladeElementTheory)
    # Configure the compute_aerodynamic_performance mock return value
    bet.compute_aerodynamic_performance.return_value = (1000.0, 2000.0, 3000.0, 0.5, 0.4)  # thrust, torque, power, ct, cp
    return bet


@pytest.fixture
def performance_analyzer(mock_blade):
    """Create a PerformanceAnalyzer instance for testing."""
    return PerformanceAnalyzer(
        blade=mock_blade,
        min_wind_speed=5.0,
        max_wind_speed=15.0,
        num_points=10,
        num_blades=3,
        rho=1.225
    )


def test_initialization(mock_blade):
    """Test that the PerformanceAnalyzer initializes correctly with various parameters."""
    analyzer = PerformanceAnalyzer(
        blade=mock_blade,
        min_wind_speed=5.0,
        max_wind_speed=15.0,
        num_points=10,
        num_blades=3,
        rho=1.225
    )
    
    assert analyzer.blade == mock_blade
    assert analyzer.min_wind_speed == 5.0
    assert analyzer.max_wind_speed == 15.0
    assert analyzer.num_points == 10
    assert analyzer.num_blades == 3
    assert analyzer.rho == 1.225
    assert len(analyzer.wind_speeds) == 10
    assert analyzer._performance_metrics is None
    assert analyzer._performance_calculated is False
    
    # Check wind speeds are correctly distributed
    assert np.isclose(analyzer.wind_speeds[0], 5.0)
    assert np.isclose(analyzer.wind_speeds[-1], 15.0)


@patch('src.PerformanceAnalyzer.OperationalCondition')
@patch('src.PerformanceAnalyzer.BladeElementTheory')
def test_calculate_performance(MockBET, MockOperationalCondition, performance_analyzer, mock_blade):
    """Test that performance calculation works correctly."""
    # Configure the mocks
    mock_op_condition = MagicMock()
    MockOperationalCondition.return_value = mock_op_condition
    
    mock_bet_instance = MagicMock()
    mock_bet_instance.compute_aerodynamic_performance.return_value = (1000.0, 2000.0, 3000.0, 0.5, 0.4)
    MockBET.return_value = mock_bet_instance
    
    # Call the method under test
    result = performance_analyzer.calculate_performance()
    
    # Verify the results
    assert performance_analyzer._performance_calculated is True
    assert len(result["wind_speed"]) == 10
    assert len(result["power"]) == 10
    assert len(result["thrust"]) == 10
    assert len(result["torque"]) == 10
    assert len(result["ct"]) == 10
    assert len(result["cp"]) == 10
    
    # Check that mocks were called correctly
    assert MockOperationalCondition.call_count == 10
    assert MockBET.call_count == 10
    assert mock_bet_instance.compute_aerodynamic_performance.call_count == 10
    assert mock_op_condition.calculate_angular_velocity.call_count == 10


def test_performance_metrics_property(performance_analyzer):
    """Test that the performance_metrics property calculates metrics if not already done."""
    with patch.object(performance_analyzer, 'calculate_performance') as mock_calculate:
        mock_calculate.return_value = {"test": "data"}
        
        # First call should trigger calculation
        performance_analyzer._performance_calculated = False
        result = performance_analyzer.performance_metrics
        
        assert mock_calculate.called
        
        # Reset mock
        mock_calculate.reset_mock()
        
        # Second call should not trigger calculation since it's already done
        performance_analyzer._performance_calculated = True
        result = performance_analyzer.performance_metrics
        
        assert not mock_calculate.called


@patch('matplotlib.pyplot.figure')
@patch('matplotlib.pyplot.plot')
@patch('matplotlib.pyplot.xlabel')
@patch('matplotlib.pyplot.ylabel')
@patch('matplotlib.pyplot.title')
@patch('matplotlib.pyplot.grid')
@patch('matplotlib.pyplot.legend')
def test_plot_power_curve(mock_legend, mock_grid, mock_title, mock_ylabel, 
                         mock_xlabel, mock_plot, mock_figure, performance_analyzer):
    """Test that plot_power_curve plots the correct data."""
    # Setup
    performance_analyzer._performance_calculated = True
    performance_analyzer._performance_metrics = {
        "wind_speed": [5, 10, 15],
        "power": [1000, 2000, 3000],
        "thrust": [500, 1000, 1500],
        "torque": [300, 600, 900],
        "ct": [0.5, 0.6, 0.7],
        "cp": [0.4, 0.5, 0.6]
    }
    
    # Call method
    performance_analyzer.plot_power_curve()
    
    # Verify calls
    mock_figure.assert_called_once()
    mock_plot.assert_called_once()
    mock_xlabel.assert_called_once_with("Wind Speed (m/s)")
    mock_ylabel.assert_called_once_with("Power (W)")
    mock_title.assert_called_once_with("Wind Turbine Power Curve")
    mock_grid.assert_called_once()
    mock_legend.assert_called_once()


@patch('matplotlib.pyplot.figure')
@patch('matplotlib.pyplot.plot')
@patch('matplotlib.pyplot.xlabel')
@patch('matplotlib.pyplot.ylabel')
@patch('matplotlib.pyplot.title')
@patch('matplotlib.pyplot.grid')
@patch('matplotlib.pyplot.legend')
def test_plot_thrust_curve(mock_legend, mock_grid, mock_title, mock_ylabel, 
                          mock_xlabel, mock_plot, mock_figure, performance_analyzer):
    """Test that plot_thrust_curve plots the correct data."""
    # Setup
    performance_analyzer._performance_calculated = True
    performance_analyzer._performance_metrics = {
        "wind_speed": [5, 10, 15],
        "power": [1000, 2000, 3000],
        "thrust": [500, 1000, 1500],
        "torque": [300, 600, 900],
        "ct": [0.5, 0.6, 0.7],
        "cp": [0.4, 0.5, 0.6]
    }
    
    # Call method
    performance_analyzer.plot_thrust_curve()
    
    # Verify calls
    mock_figure.assert_called_once()
    mock_plot.assert_called_once()
    mock_xlabel.assert_called_once_with("Wind Speed (m/s)")
    mock_ylabel.assert_called_once_with("Thrust (N)")
    mock_title.assert_called_once_with("Wind Turbine Thrust Curve")
    mock_grid.assert_called_once()
    mock_legend.assert_called_once()


@patch('matplotlib.pyplot.figure')
@patch('matplotlib.pyplot.plot')
@patch('matplotlib.pyplot.xlabel')
@patch('matplotlib.pyplot.ylabel')
@patch('matplotlib.pyplot.title')
@patch('matplotlib.pyplot.grid')
@patch('matplotlib.pyplot.legend')
def test_plot_torque_curve(mock_legend, mock_grid, mock_title, mock_ylabel, 
                          mock_xlabel, mock_plot, mock_figure, performance_analyzer):
    """Test that plot_torque_curve plots the correct data."""
    # Setup
    performance_analyzer._performance_calculated = True
    performance_analyzer._performance_metrics = {
        "wind_speed": [5, 10, 15],
        "power": [1000, 2000, 3000],
        "thrust": [500, 1000, 1500],
        "torque": [300, 600, 900],
        "ct": [0.5, 0.6, 0.7],
        "cp": [0.4, 0.5, 0.6]
    }
    
    # Call method
    performance_analyzer.plot_torque_curve()
    
    # Verify calls
    mock_figure.assert_called_once()
    mock_plot.assert_called_once()
    mock_xlabel.assert_called_once_with("Wind Speed (m/s)")
    mock_ylabel.assert_called_once_with("Torque (Nm)")
    mock_title.assert_called_once_with("Wind Turbine Torque Curve")
    mock_grid.assert_called_once()
    mock_legend.assert_called_once()


def test_ensure_performance_calculated(performance_analyzer):
    """Test that _ensure_performance_calculated calls calculate_performance when needed."""
    with patch.object(performance_analyzer, 'calculate_performance') as mock_calculate:
        # Should call calculate_performance when not calculated
        performance_analyzer._performance_calculated = False
        performance_analyzer._ensure_performance_calculated()
        assert mock_calculate.called
        
        # Reset mock
        mock_calculate.reset_mock()
        
        # Should not call calculate_performance when already calculated
        performance_analyzer._performance_calculated = True
        performance_analyzer._ensure_performance_calculated()
        assert not mock_calculate.called