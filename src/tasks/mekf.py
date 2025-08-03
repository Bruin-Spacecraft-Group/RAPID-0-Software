"""
Determines an estimate of the attitude of the RAPID-0 satellite using a Multiplicative Extended Kalman Filter (MEKF).
"""

import ulab.numpy as np  # type: ignore
from quaternion import Quaternion


def mekf_update(q_ref: Quaternion, w_ref: np.ndarray, dt: float) -> Quaternion:
    """
    Calculates the attitude using a Multiplicative Extended Kalman Filter (MEKF) based on:
    'Multiplicative vs. Additive Filtering for Spacecraft Attitude Determination' (Markley, 2003)

    Args:
        q_ref (Quaternion): Body reference quaternion which the calculations are based on. The closer ref is to the actual attitude,
                            the less error resulting from the MEKF. Assumed starting basis for which w_ref acts on
        w_ref (np.ndarray): Angular acceleration vector in the body reference
        dt (float): Amount of time that has passed since a new estimate for q_ref has been made (in ms?)

    Returns:
        Quaternion: The estimated attitude Quaternion from the body frame to the inertial frame
    """

    omega_q = Quaternion(0.0, *w_ref, normalize=False)
    q_prop = (q_ref + 0.5 * dt * (omega_q * q_ref)).normalize()

    return q_prop
