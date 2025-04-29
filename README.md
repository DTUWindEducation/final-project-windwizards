[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zjSXGKeR)

# Wind Turbine BEM Modeling Package

Team: WindyWizards

## Overview

This package implements a Blade Element Momentum (BEM) model to predict the aerodynamic performance of wind turbines. It can:

- Load and process airfoil geometry and polar data
- Calculate aerodynamic coefficients at different operating conditions
- Compute induction factors through iterative BEM solution
- Generate 3D visualizations of blade geometry
- Calculate power and thrust coefficients
- Analyze turbine performance across operational conditions

The implementation is based on the IEA 15-MW reference wind turbine specifications and follows the BEM theory as described in Hansen (2015).

## Quick-start guide

1. Install the package:
```bash
pip install -e .
```

2. Run the example:
```bash
python examples/main.py
```

This will:
- Load the IEA 15-MW reference turbine data
- Process airfoil data
- Calculate performance metrics
- Generate visualization plots

## Architecture

Below is the architecture diagram for the package: 


   ```
   [BEM_solver]
   ├── inputs/
   │   ├── IEA-15-240-RWT/
   │   │   ├── airfoil_data/
   │   │   ├── blade_geometry/
   │   │   └── operational_conditions/
   │   └── Your_Data/
   ├── outputs/
   │   ├── performance_results/
   │   └── visualization_plots/
   ├── src/
   │   ├── Airfoil.py
   │   ├── BladeElement.py
   │   ├── Blade.py
   │   ├── OperationalCondition.py
   │   ├── BladeElementTheory.py
   │   └── PerformanceAnalyzer.py
   ├── tests/
   │   ├── test_airfoil.py
   │   ├── test_blade.py
   │   ├── test_operational_condition.py
   │   └── other_test_scripts/
   ├── examples/
   │   ├── main.py
   │   └── additional_examples/
   ├── .gitignore
   ├── LICENSE
   ├── Collaboration.md
   ├── README.md
   ├── pyproject.toml
   └── other_optional_files/
   ```
   
The Code architecture diagram is illustrating the relationships between the key components:

![Architecture Diagram](Architecture_Diagram.png)

This diagram provides a visual representation of how the classes interact and the overall structure of the package.

The program workflow is:
1. Initialize blade with operational characteristics
2. Load blade geometry and airfoil data
3. Set operational conditions
4. Compute induction factors
5. Calculate aerodynamic performance
6. Analyze and visualize results


## Class description

The package follows an object-oriented design with the following key components:

1. **Airfoil**: Manages airfoil geometry and aerodynamic data
   - Loading coordinate data
   - Storing/interpolating lift/drag coefficients
   - File: `src/Airfoil.py`

2. **BladeElement**: Represents a blade section
   - Geometric properties (radius, twist, chord)
   - Local aerodynamic calculations
   - File: `src/BladeElement.py`

3. **Blade**: Manages blade assembly and calculations
   - Collection of blade elements
   - Loading blade geometry
   - Computing induction factors
   - File: `src/Blade.py`

4. **OperationalCondition**: Defines operating state
   - Wind speed
   - Air density
   - Angular velocity
   - File: `src/OperationalCondition.py`

5. **BladeElementTheory**: Implements BEM calculations
   - Iterative solution for induction factors
   - Force and moment computations
   - File: `src/BladeElementTheory.py`

6. **PerformanceAnalyzer**: High-level analysis tools
   - Power curve calculations
   - Performance optimization
   - Results visualization
   - File: `src/PerformanceAnalyzer.py`


