"""
Determines an estimate of the attitude of the RAPID-0 satellite using a Multiplicative Extended Kalman Filter (MEKF).
"""

import ulab.numpy as np  # type: ignore
from quaternion import Quaternion


def neg_skew(w: np.ndarray):
    return np.ndarray([[0, w[2], -w[1]], [-w[2], 0, w[0]], [w[1], -w[0], 0]])


def mekf_update(
    q_ref: Quaternion, w_ref: np.ndarray, P: np.ndarray, Q_noise: np.ndarray, dt: float
) -> Quaternion:
    """
    Calculates the attitude using a Multiplicative Extended Kalman Filter (MEKF) based on:
    'Multiplicative vs. Additive Filtering for Spacecraft Attitude Determination' (Markley, 2003)

    Args:
        q_ref (Quaternion): Body reference quaternion which the calculations are based on. The closer ref is to the actual attitude,
                            the less error resulting from the MEKF. Assumed starting basis for which w_ref acts on
        w_ref (np.ndarray): Angular acceleration vector in the body reference
        P (np.ndarray): 3x3 Covariance matrix (ensure this isn't the 0 matrix when starting or the filter won't update effectively)
        Q_noise: 3x3 Diagonal matrix representing noise/bias from the gyro sensor
        dt (float): Amount of time that has passed since a new estimate for q_ref has been made (in ms?)

    Returns:
        Quaternion: The estimated attitude Quaternion from the body frame to the inertial frame
    """

    # Equation (9) from Markley paper
    omega_q = Quaternion(0.0, *w_ref, normalize=False)
    q = (q_ref + (0.5 * dt * (omega_q * q_ref))).normalize()

    # Equation (14) from Markley paper
    F_a = neg_skew(w_ref)
    G = np.eye(3)
    P = (
        P + (np.dot(P, F) + np.dot(P, -F) + np.dot(G, np.dot(Q_noise, G))) * dt
    )  # If G is just identity matrix, can reduce dot operations

    return q
