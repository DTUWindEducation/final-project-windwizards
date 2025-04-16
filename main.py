from pathlib import Path
from src.Airfoil import Airfoil
from src.Blade import Blade
from src.OperationalConditions import OperationalConditions
from src.Airfoil import plot_airfoil_shapes

if __name__ == "__main__":
    base_path = Path(__file__).parent / "inputs/IEA-15-240-RWT"

    print("Loading airfoils...")
    airfoil_map = {}

    for i in range(50):
        idx = f"{i:02d}"
        coord_file = base_path / f"Airfoils/IEA-15-240-RWT_AF{idx}_Coords.txt"
        polar_file = base_path / f"Airfoils/IEA-15-240-RWT_AeroDyn15_Polar_{idx}.dat"

        airfoil = Airfoil.from_polar_and_coords(coord_file, polar_file)
        airfoil_map[i] = airfoil

    print(f"Loaded {len(airfoil_map)} airfoils")

    print("Loading blade...")
    blade_file = base_path / "IEA-15-240-RWT_AeroDyn15_blade.dat"
    blade = Blade.from_file(blade_file, airfoil_map)
    print(f"Loaded blade with {len(blade.elements)} elements")

    print("Loading operational conditions...")
    opt_file = base_path / "IEA_15MW_RWT_Onshore.opt"
    ops = OperationalConditions.from_file(opt_file)
    print(f"Loaded {len(ops.conditions)} operational conditions")

    print("\nFirst blade element:")
    print(blade.elements[0])

    print("\nFirst operational condition:")
    print(ops.conditions[0])

    print("\nFirst airfoil summary:")
    print(airfoil_map[0])

    print("\nPlotting selected airfoil shapes...")
    airfoil_indices = [0, 4, 9, 14, 19, 24, 29, 34, 39, 44, 49]
    plot_airfoil_shapes(base_path / "Airfoils", airfoil_indices)
