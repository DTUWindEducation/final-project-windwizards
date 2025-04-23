import numpy as np
from src.Blade import Blade
from src.BladeElementTheory import BladeElementTheory

class PerformanceAnalyzer:
    def __init__(self, blade: Blade, min_wind_speed: float = 0.0, max_wind_speed: float = 25.0, num_points: int = 100):
        """
        Initialize PerformanceAnalyzer with a blade object.
        
        Parameters:
        - blade (Blade): Blade object containing geometry and operational conditions
        """
        self.blade = blade
