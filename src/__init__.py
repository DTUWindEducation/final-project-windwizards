""" Source code for small functions used in the project. """

import numpy as np  

def  calculate_solidity(chord_length, radius, num_blades):
    """
    Calculate the solidity of a blade element.

    Parameters:
    - chord_length (float): Chord length of the blade element [m].
    - radius (float): Radius of the blade element [m].
    - num_blades (int): Number of blades.

    Returns:
    - solidity (float): Solidity of the blade element.
    """
    return (num_blades * chord_length) / (2 * np.pi * radius)



