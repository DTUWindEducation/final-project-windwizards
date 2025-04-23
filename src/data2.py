import math
import numpy as np

class Blade:
    def __init__(self, BladeGeometry, OperationalConditions):
        """
        Initialize the Blade class with blade geometry and operational conditions.
        
        Parameters:
        BladeGeometry (array of BladeGeometry): An array of BladeGeometry class containing blade properties.
        OperationalConditions (OperationalConditions): An instance of the OperationalConditions class containing operational parameters.
        """
        self.blade_geometries = BladeGeometry
        self.operational_conditions = OperationalConditions


    def compute_local_angle_of_attack(self, initial_a=0):
        blade in self.blade_geometries:
        V = self.operational_conditions.wind_speed
        return phi - twist - pitch_angle



class BladeGeometry:
    def __init__(self, radius, hub_radius, r_sections, chord, twist, airfoil_data):
        self.radius = radius
        self.hub_radius = hub_radius
        self.r_sections = r_sections
        self.chord = chord
        self.twist = twist
        self.airfoil_data = airfoil_data

    def get_section_properties(self, i):
        return (self.r_sections[i], self.chord[i], self.twist[i], self.airfoil_data[i])

class OperationalConditions:
    def __init__(self, wind_speed, rotor_speed, pitch_angle, air_density=1.225):
        self.wind_speed = wind_speed
        self.rotor_speed = rotor_speed
        self.pitch_angle = pitch_angle
        self.air_density = air_density

    def get_tip_speed_ratio(self, radius):
        return (self.rotor_speed * radius) / self.wind_speed


class MomentumTheory:
    def compute_induction_factors(self, a_guess, a_prime_guess, phi, solidity, Cn, Ct):
        a, a_prime = a_guess, a_prime_guess
        for _ in range(100):  # Fixed-point iteration
            a_new = 1 / (1 + (4 * math.sin(phi)**2) / (solidity * Cn))
            a_prime_new = 1 / (1 + (4 * math.sin(phi) * math.cos(phi)) / (solidity * Ct))
            if abs(a - a_new) < 1e-5 and abs(a_prime - a_prime_new) < 1e-5:
                break
            a, a_prime = a_new, a_prime_new
        return a, a_prime


class BladeElementTheory:
    def compute_local_angle_of_attack(self, phi, twist, pitch_angle):
        return phi - twist - pitch_angle

    def compute_forces(self, alpha, chord, V_rel, airfoil_data):
        Cl = np.interp(alpha, airfoil_data['alpha'], airfoil_data['Cl'])
        Cd = np.interp(alpha, airfoil_data['alpha'], airfoil_data['Cd'])
        Cn = Cl * math.cos(alpha) + Cd * math.sin(alpha)
        Ct = Cl * math.sin(alpha) - Cd * math.cos(alpha)
        return Cl, Cd, Cn, Ct


class BEMSolver:
    def __init__(self, blade, ops, tolerance=1e-5, max_iterations=100):
        self.blade = blade
        self.ops = ops
        self.tolerance = tolerance
        self.max_iterations = max_iterations

    def solve_section(self, i):
        r, chord, twist, airfoil_data = self.blade.get_section_properties(i)
        phi = math.atan(self.ops.wind_speed / (self.ops.rotor_speed * r))
        solidity = (chord * self.blade.radius) / (2 * math.pi * r)
        a, a_prime = 0.3, 0.01  # Initial guesses
        bem = MomentumTheory()
        bet = BladeElementTheory()

        for _ in range(self.max_iterations):
            alpha = bet.compute_local_angle_of_attack(phi, twist, self.ops.pitch_angle)
            Cl, Cd, Cn, Ct = bet.compute_forces(alpha, chord, self.ops.wind_speed, airfoil_data)
            a_new, a_prime_new = bem.compute_induction_factors(a, a_prime, phi, solidity, Cn, Ct)
            if abs(a - a_new) < self.tolerance and abs(a_prime - a_prime_new) < self.tolerance:
                break
            a, a_prime = a_new, a_prime_new

        return a, a_prime, Cn, Ct

    def solve(self):
        results = []
        for i in range(len(self.blade.r_sections)):
            results.append(self.solve_section(i))
        return results


class PerformanceMetrics:
    def compute_thrust(self, Fn_list):
        return sum(Fn_list)

    def compute_torque(self, Ft_list, r_list):
        return sum(Ft * r for Ft, r in zip(Ft_list, r_list))

    def compute_power(self, torque, rotor_speed):
        return torque * rotor_speed


#__________________________________________________________
def test_blade_geometry():
    # Test data
    radius = 50
    hub_radius = 5
    r_sections = [10, 20, 30, 40, 50]
    chord = [3, 3.5, 4, 4.5, 5]
    twist = [10, 8, 6, 4, 2]
    airfoil_data = [
        {'alpha': [0, 5, 10], 'Cl': [0.1, 0.5, 1.0], 'Cd': [0.01, 0.02, 0.03]},
        {'alpha': [0, 5, 10], 'Cl': [0.2, 0.6, 1.1], 'Cd': [0.02, 0.03, 0.04]},
        {'alpha': [0, 5, 10], 'Cl': [0.3, 0.7, 1.2], 'Cd': [0.03, 0.04, 0.05]},
        {'alpha': [0, 5, 10], 'Cl': [0.4, 0.8, 1.3], 'Cd': [0.04, 0.05, 0.06]},
        {'alpha': [0, 5, 10], 'Cl': [0.5, 0.9, 1.4], 'Cd': [0.05, 0.06, 0.07]},
    ]

    # Create BladeGeometry instance
    blade = BladeGeometry(radius, hub_radius, r_sections, chord, twist, airfoil_data)

    # Test get_section_properties
    for i in range(len(r_sections)):
        r, c, t, af_data = blade.get_section_properties(i)
        assert r == r_sections[i], f"Expected r={r_sections[i]}, got {r}"
        assert c == chord[i], f"Expected chord={chord[i]}, got {c}"
        assert t == twist[i], f"Expected twist={twist[i]}, got {t}"
        assert af_data == airfoil_data[i], f"Expected airfoil_data={airfoil_data[i]}, got {af_data}"

    print("BladeGeometry tests passed.")

# Run the test
test_blade_geometry()