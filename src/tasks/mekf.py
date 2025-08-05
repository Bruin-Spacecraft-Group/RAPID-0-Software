"""
Determines an estimate of the attitude of the RAPID-0 satellite using a Multiplicative Extended Kalman Filter (MEKF).
"""

# TODO: Check signage of quaternion operations and - vs + skew

import ulab.numpy as np  # type: ignore
from quaternion import Quaternion


def skew(w: np.ndarray):
    return np.ndarray([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def mekf_update(
    q_ref: Quaternion,
    w_ref: np.ndarray,
    P: np.ndarray,
    Q_noise: np.ndarray,
    v_body: np.ndarray,
    v_inertial: np.ndarray,
    dt: float,
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
        v_body: Measured vector from body frame (from magnetometer or sun sensor)
        v_inertial: Expected vector measurement at Quaternion(1,0,0,0) orientation
        dt (float): Amount of time that has passed since a new estimate for q_ref has been made (in ms?)

    Returns:
        Quaternion: The estimated attitude Quaternion from the body frame to the inertial frame
    """

    # Step 1: Calculate expected quaternion from kinematics
    # Equation (9) from Markley paper
    omega_q = Quaternion(0.0, *w_ref, normalize=False)
    q = (q_ref + (0.5 * dt * (omega_q * q_ref))).normalize()

    # Step 2: Calculate covariance matrix
    # Equation (14) from Markley paper
    F_a = skew(w_ref)
    G = np.eye(3)
    P = (
        P + (np.dot(F, P) + np.dot(P, -F) + np.dot(G, np.dot(Q_noise, G))) * dt
    )  # If G is just identity matrix, can reduce dot operations

    # Step 3: Predict measured vector
    # Equation (18) from Markley paper
    v_pred = q_ref.rotate_vector(v_inertial)

    # Step 4: Measurement matrix (Jacobian)
    # Equation (19) from Markley paper
    H = skew(v_pred)

    return q
