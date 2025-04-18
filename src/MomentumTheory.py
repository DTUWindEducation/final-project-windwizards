""" Momentum-Theory
Compute axial (a) and tangential (a') induction factors using actuator disk theory.
"""

import numpy as np

class MomentumTheory:
    def __init__(self, a_guess, a_prime_guess, phi, solidity, Cn, Ct, max_iterations = 100,  tolerance = 1e-5):
        """
        Initialize the MomentumTheory class with parameters.

        Parameters:
        - a_guess (float): Initial guess for axial induction factor.
        - a_prime_guess (float): Initial guess for tangential induction factor.
        - phi (float): Flow angle [rad].
        - solidity (float): Local solidity of the blade element.
        - Cn (float): Normal force coefficient.
        - Ct (float): Tangential force coefficient.
        """
        self.a = a_guess
        self.a_prime = a_prime_guess
        self.phi = phi
        self.solidity = solidity
        self.Cn = Cn
        self.Ct = Ct
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def compute_induction_factors(self):
        """
        Compute axial (a) and tangential (a') induction factors using actuator disk theory.

        Returns:
        - a (float): Axial induction factor.
        - a_prime (float): Tangential induction factor.
        """

        for _ in range(self.max_iterations):
            # Update axial induction factor
            a_new = 1 / (1 + (4 * np.sin(self.phi)**2) / (self.solidity * self.Cn))
            
            # Update tangential induction factor
            a_prime_new = 1 / (1 + (4 * np.sin(self.phi) * np.cos(self.phi)) / (self.solidity * self.Ct))
            
            # Check for convergence
            if abs(self.a - a_new) < self.tolerance and abs(self.a_prime - a_prime_new) < tolerance:
                break
            
            self.a, self.a_prime = a_new, a_prime_new

        return self.a, self.a_prime


