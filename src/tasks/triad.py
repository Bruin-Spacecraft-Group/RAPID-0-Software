"""
Determines the attitude of the RAPID-0 satellite with two vectors from sensors.
"""


import ulab.numpy as np
from quaternion import Quaternion


def triad_algorithm(r1: np.ndarray, r2: np.ndarray, b1: np.ndarray, b2: np.ndarray) -> Quaternion:
    """
    Calculates the attitude using an optimized TRIAD algorithm based off of:
    'Fast Quaternion Attitude Estimation From Two Vector Measurements' (Markley, 2002).

    Args:
        r1 (np.ndarray): The first (more accurate) reference vector in the inertial frame (e.g. Sun vector from environment model).
        r2 (np.ndarray): The second (less accurate) reference vector in the inertial frame (e.g. Magnetic field from environment model).
        b1 (np.ndarray): The measurement of the first vector in the body frame (e.g. Sun sensor reading).
        b2 (np.ndarray): The measurement of the second vector in the body frame (e.g. Magnetometer reading).

    Returns:
        Quaternion: The estimated attitude Quaternion from the body frame to the inertial frame (or an
                    identity Quaternion if calculation is impossible with the given input vectors).
    """

    # Normalize input vectors
    r1_unit = r1 / np.linalg.norm(r1)
    r2_unit = r2 / np.linalg.norm(r2)
    b1_unit = b1 / np.linalg.norm(b1)
    b2_unit = b2 / np.linalg.norm(b2)

    # Calculate intermediate cross products (note that these are not normalized to improve computation time)
    r3 = np.cross(r1_unit, r2_unit)
    b3 = np.cross(b1_unit, b2_unit)

    # Check for collinearity (which gives a zero cross product and makes finding a solution impossible for the given input)
    if np.linalg.norm(b3) < 1e-9 or np.linalg.norm(r3) < 1e-9:
        return Quaternion()

    # Check if b1 and r1 are anti-parallel (to prevent division by zero)
    dot_b1_r1 = np.dot(b1_unit, r1_unit)
    one_plus_dot = 1.0 + dot_b1_r1
    if one_plus_dot < 1e-9:
        return Quaternion()

    # Eq. (31) from the Markley 2002 paper
    mu = one_plus_dot*np.dot(b3, r3) - np.dot(b1_unit, r3)*np.dot(r1_unit, b3)

    b1_plus_r1 = b1_unit + r1_unit
    nu = np.dot(b1_plus_r1, np.cross(b3, r3)) # Eq. (32) from the Markley paper

    rho = np.sqrt(mu**2 + nu**2) # Eq. (33) from the Markley paper

    # If rho is near zero, then mu and nu are also near zero
    if rho < 1e-9:
        return Quaternion()

    if mu >= 0: # Eq. (35a) from the Markley paper
        rho_plus_mu = rho + mu
        
        # Calculate the square root term in the denominator of the scalar multiple
        sqrt_term = rho * rho_plus_mu * one_plus_dot
        if sqrt_term < 1e-9: # Prevent division by zero
            return Quaternion()
        
        # The scalar multiple
        mult = 0.5 / np.sqrt(sqrt_term) 
        
        # The scalar part of the quaternion
        w = rho_plus_mu * one_plus_dot

        # The vector part of the quaternion
        v = rho_plus_mu*np.cross(b1_unit, r1_unit) + nu*b1_plus_r1

        # Instantiate the estimated attitude Quaternion
        q = Quaternion(w*mult, v[0]*mult, v[1]*mult, v[2]*mult)

    else: # Eq. (35b) from the Markley paper
        rho_minus_mu = rho - mu
        
        # Calculate the square root term in the denominator of the scalar multiple
        sqrt_term = rho * rho_minus_mu * one_plus_dot
        if sqrt_term < 1e-9: # Prevent division by zero
            return Quaternion()

        # The scalar multiple
        mult = 0.5 / np.sqrt(sqrt_term)

        # The scalar part of the quaternion
        w = nu * one_plus_dot

        # The vector part of the quaternion
        v = nu*np.cross(b1_unit, r1_unit) + rho_minus_mu*b1_plus_r1

        # Instantiate the estimated attitude Quaternion
        q = Quaternion(w*mult, v[0]*mult, v[1]*mult, v[2]*mult)

    return q
