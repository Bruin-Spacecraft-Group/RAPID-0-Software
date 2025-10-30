"""
Determine an estimate of the attitude of the RAPID-0 satellite using a 
Multiplicative Extended Kalman Filter (MEKF).
"""

# TODO: Create constants for constant matricies

import ulab.numpy as np  # type: ignore
from quaternion import Quaternion

class StateEstimate:
    """
    Current Estimated State class + covariance as state uncertainty

    q_ref (Quaternion): Body reference quaternion which the calculations are based on. 
                        The closer ref is to the actual attitude, the less error resulting 
                        from the MEKF. Assumed starting basis for which w_ref acts on
    w_ref (np.ndarray): Angular acceleration vector in the body reference from gyroscopes
    cv_matrix (np.ndarray): [Previously P] 3x3 Covariance matrix (ensure this isn't the 0 
                             matrix when starting or the filter won't update effectively)
    """

    def __init__(self, q_ref, w_ref, cv_matrix):
        self.q_ref: Quaternion = q_ref
        self.w_ref: np.ndarray = w_ref
        self.cv_matrix: np.ndarray = cv_matrix

class SensorMeasurement:
    """
    Sensor Measurement class + Noise/bias matrices as sensor uncertainty

    gyro_noise: [previously Q_noise] 3x3 Diagonal matrix representing noise/bias from the 
                gyro sensor (given as sigma^2 * I_3)
    measurement_noise: [previously R_meas] 3x3 Diagonal matrix representing noise/bias from 
                       the measured body vector (given as sigma^2 * I_3)
    v_body: Measured vector from body frame (from magnetometer or sun sensor)
    v_inertial: Expected vector measurement at Quaternion(1,0,0,0) orientation
    
    """

    def __init__(self, gyro_noise, r_meas, v_body, v_inertial):
        self.gyro_noise = gyro_noise
        self.r_meas = r_meas
        self.v_body = v_body
        self.v_inertial = v_inertial

def skew(w: np.ndarray):
    """
    Returns a 3x3 skew (/cross product) matrix built from an input 3-element vector

    Args:
        w (np.ndarray): (3,) 3-element vector

    Returns:
        np.ndarray: 3x3 skew/cross-product matrix
        [[  0,   w[2], w[1]],
         [ w[2],  0,  -w[0]],
         [-w[1], w[0],  0 ]]
    """
    return np.ndarray([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])

# pylint: disable=invalid-name
def mekf_update(
    state: StateEstimate,
    measurement: SensorMeasurement,
    dt: float,
) -> Quaternion:
    """
    Calculates the attitude using a Multiplicative Extended Kalman Filter (MEKF) based on:
    'Multiplicative vs. Additive Filtering for Spacecraft Attitude Determination' (Markley, 2003)

    Args:
        state (StateEstimate): Current state, encapsulates state q, angular acceleration, and
                               3x3 covariance matrix as uncertainty
        measurement (SensorMeasurement): Measurement object, encapsulates measurements and their 
                                         3x3 noise matrices
        dt (float): Amount of time that has passed since a new estimate for q_ref has been made (ms)

    Returns:
        Quaternion: The estimated attitude Quaternion from the body frame to the inertial frame
    """

    # Renaming long variables
    P = state.cv_matrix

    # Step 1: Calculate expected quaternion from kinematics
    # Equation (9) from Markley paper
    omega_q = Quaternion(0.0, *state.w_ref)
    state.q_ref += 0.5 * dt * (omega_q * state.q_ref)

    # Step 2: Predict measured vector
    # Equation (18) from Markley paper
    v_pred = state.q_ref.rotate_vector(measurement.v_inertial)

    # Step 3: Measurement matrix (Jacobian)
    # Equation (19) from Markley paper
    H = skew(v_pred)

    # Step 4: Calculate covariance matrix
    # Equation (14) from Markley paper
    F_a = -skew(state.w_ref)
    G = np.eye(3)
    # Equation (21) from Markley paper
    P += (
        np.dot(F_a, P)
        + np.dot(P, -F_a)
        + np.dot(G, np.dot(measurement.gyro_noise, G))
        - np.dot(P, np.dot(-H, np.dot(np.linalg.inv(measurement.r_meas), np.dot(H, P))))
    ) * dt
    # If G is just identity matrix, can reduce dot operations
    # Remember that the negative of skew is the transpose of the matrix

    # TODO: Double check this part and following parts are right
    # Step 5: Kalman Gain
    # Equation (22) from Markley paper(?)
    S = np.dot(H, np.dot(P, -H)) + measurement.r_meas
    K = np.dot(
        P, np.dot(-H, np.linalg.inv(S))
    )  # TODO: Calculating the inverse matrix can result in singularities, should check

    # Step 6: Delta_a calculation
    v_perp = measurement.v_body - v_pred
    delta_a = np.dot(K, v_perp)  # 3x1 correction vector a

    # Step 7: Covariance update
    I = np.eye(3)
    P = np.dot(I - np.dot(K, H), P)

    # Step 8: Apply attitude correction using small-angle approximation
    # Equation (6) and (7) from Markley paper
    dq = Quaternion(1.0, *(0.5 * delta_a))
    state.q_ref = dq * state.q_ref
    state.q_ref.normalize()

    return state.q_ref
