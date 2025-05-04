from typing import Optional
import numpy as np


class BladeElement:
    """
    Represents a blade element in a wind turbine blade.

    Attributes:
        r (float): Spanwise position [m].
        twist (float): Twist angle [deg].
        chord (float): Chord length [m].
        airfoil_id (int): Airfoil index from file.
        airfoil (Optional['Airfoil']): Associated airfoil object (optional).
        a (Optional[float]): Axial induction factor.
        a_prime (Optional[float]): Tangential induction factor.
        Cn (Optional[float]): Normal force coefficient.
        Ct (Optional[float]): Tangential force coefficient.
        cl (Optional[float]): Lift coefficient.
        cd (Optional[float]): Drag coefficient.
        alpha (Optional[float]): Angle of attack [rad].
        phi (Optional[float]): Flow angle [rad].
        dr (Optional[float]): Elemental radius [m].
        dT (Optional[float]): Elemental thrust [N].
        dM (Optional[float]): Elemental moment [Nm].
        L (Optional[float]): Lift force [N].
        D (Optional[float]): Drag force [N].
        Fn (Optional[float]): Normal force [N].
        Ft (Optional[float]): Tangential force [N].
        V_rel (Optional[float]): Relative wind speed [m/s].
        solidity (Optional[float]): Solidity of the blade element.
    """

    def __init__(
        self,
        r: float,
        twist: float,
        chord: float,
        airfoil_id: int,
        airfoil: Optional["Airfoil"] = None,
    ):
        """
        Initializes a BladeElement object.

        Args:
            r (float): Spanwise position [m].
            twist (float): Twist angle [deg].
            chord (float): Chord length [m].
            airfoil_id (int): Airfoil index from file.
            airfoil (Optional['Airfoil']): Associated airfoil object (optional).
        """
        self.r = r
        self.twist = twist
        self.chord = chord
        self.airfoil_id = airfoil_id
        self.airfoil = airfoil
        self.a = None
        self.a_prime = None
        self.Cn = None
        self.Ct = None
        self.cl = None
        self.cd = None
        self.alpha = None
        self.phi = None
        self.dr = None
        self.dT = None
        self.dM = None
        self.L = None
        self.D = None
        self.Fn = None
        self.Ft = None
        self.V_rel = None
        self.solidity = None

    def calculate_solidity(self, operational_conditions=None):
        """
        Calculates the solidity of the blade element.

        Args:
            operational_conditions: Operational conditions containing the number of blades.

        Returns:
            float: Solidity of the blade element.
        """
        num_blades = operational_conditions.num_blades

        if self.r == 0:
            self.solidity = 1
            return self.solidity

        solidity = (num_blades * self.chord) / (2 * np.pi * self.r)
        # Solidity cannot exceed 1 for physical reasons
        solidity = min(solidity, 1)
        self.solidity = solidity
        return self.solidity

    def compute_element_induction_factors(
        self,
        a,
        a_prime,
        wind_speed,
        omega,
        r,
        phi,
        Cn,
        Ct,
        tolerance=1e-5,
        max_iterations=100,
    ):
        """
        Computes the induction factors for a single blade element.

        Args:
            a (float): Initial axial induction factor.
            a_prime (float): Initial tangential induction factor.
            wind_speed (float): Wind speed [m/s].
            omega (float): Rotational speed [rad/s].
            r (float): Spanwise position [m].
            phi (float): Flow angle [rad].
            Cn (float): Normal force coefficient.
            Ct (float): Tangential force coefficient.
            tolerance (float): Convergence tolerance.
            max_iterations (int): Maximum number of iterations.

        Returns:
            tuple: Axial and tangential induction factors (a, a_prime).
        """
        for _ in range(max_iterations):
            phi = np.arctan2((1 - a) * wind_speed, (1 + a_prime) * omega * r)

            a_new = 1 / ((4 * np.sin(phi) ** 2) / (self.solidity * Cn) + 1)
            a_prime_new = 1 / ((4 * np.sin(phi) * np.cos(phi)
                                ) / (self.solidity * Ct) - 1)

            if abs(
                a -
                a_new) < tolerance and abs(
                a_prime -
                    a_prime_new) < tolerance:
                break

            a, a_prime = a_new, a_prime_new

        return a, a_prime

    def compute_induction_factors(
        self,
        a_guess=0.0,
        a_prime_guess=0.0,
        max_iterations=100,
        tolerance=1e-5,
        operational_characteristics=None,
        operational_condition=None,
    ):
        """
        Computes the induction factors for the blade element.

        Args:
            a_guess (float): Initial guess for axial induction factor.
            a_prime_guess (float): Initial guess for tangential induction factor.
            max_iterations (int): Maximum number of iterations.
            tolerance (float): Convergence tolerance.
            operational_characteristics: Operational characteristics of the turbine.
            operational_condition: Current operational condition.

        Returns:
            tuple: Axial induction factor, tangential induction factor, angle of attack, lift coefficient,
                   drag coefficient, flow angle, normal force coefficient, tangential force coefficient.
        """
        a = a_guess
        a_prime = a_prime_guess
        wind_speed = operational_condition.wind_speed
        omega = operational_condition.omega
        r = self.r
        phi = np.arctan2((1 - a) * wind_speed, (1 + a_prime) * omega * r)

        if self.airfoil and self.airfoil.aero_data:
            twist_rad = np.radians(self.twist)

            wind_speeds = np.array(
                [op.wind_speed for op in operational_characteristics.characteristics]
            )
            pitches = np.array(
                [np.radians(op.pitch) for op in operational_characteristics.characteristics]
            )
            pitch_rad = np.interp(
                operational_condition.wind_speed,
                wind_speeds,
                pitches)

            alpha = phi - (pitch_rad + twist_rad)

            aero_data = self.airfoil.aero_data
            alphas = np.array([data.alpha for data in aero_data])
            cls = np.array([data.cl for data in aero_data])
            cds = np.array([data.cd for data in aero_data])

            Cl = np.interp(np.degrees(alpha), alphas, cls)
            Cd = np.interp(np.degrees(alpha), alphas, cds)

            Cn = Cl * np.cos(phi) + Cd * np.sin(phi)
            Ct = Cl * np.sin(phi) - Cd * np.cos(phi)

            a, a_prime = self.compute_element_induction_factors(
                a,
                a_prime,
                wind_speed,
                omega,
                r,
                phi,
                Cn,
                Ct,
                tolerance,
                max_iterations,
            )

            phi = np.arctan2((1 - a) * wind_speed, (1 + a_prime) * omega * r)

            self.alpha = alpha
            self.cl = Cl
            self.cd = Cd
            self.a = a
            self.a_prime = a_prime
            self.phi = phi
            self.Cn = Cn
            self.Ct = Ct

        return (
            self.a,
            self.a_prime,
            self.alpha,
            self.cl,
            self.cd,
            self.phi,
            self.Cn,
            self.Ct,
        )

    def __repr__(self):
        """
        Returns a string representation of the BladeElement object.

        Returns:
            str: String representation of the BladeElement object.
        """
        return (
            f"BladeElement(r={
                self.r}, twist={
                self.twist}, chord={
                self.chord}, " f"airfoil_id={
                    self.airfoil_id}, airfoil={
                        'Assigned' if self.airfoil else 'None'})")
