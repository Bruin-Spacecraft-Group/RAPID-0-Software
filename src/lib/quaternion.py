"""
Functions and variables used by ADCS for rotations with quaternions.
"""

import math

try:
    import ulab.numpy as np  # For CircuitPython
except ImportError:
    import numpy as np  # For GitHub Actions / PC testing


class Quaternion:
    """
    Represents a quaternion for 3D rotations with methods for multiplication,
    conjugation, normalization, and vector rotation.
    """

    def __init__(self, w=1.0, x=0.0, y=0.0, z=0.0):
        self.w = float(w)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        """
        Enables addition of two Quaternion objects (self + other)
        Important to note this is NOT the same as combining the rotations from both quaternions into a single quaternion
        """
        w = self.w + other.w
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Quaternion(w, x, y, z)

    def __rmul__(self, scalar):
        """Enables multiplying a quaternion by a scalar"""
        return Quaternion(
            scalar * self.w,
            scalar * self.x,
            scalar * self.y,
            scalar * self.z,
        )

    def __mul__(self, other):
        """Enables multiplication of two Quaternion objects (self * other)."""
        w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
        x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
        y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
        z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        return Quaternion(w, x, y, z)

    def conjugate(self):
        """Returns conjugate of the quaternion"""
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def magnitude(self):
        """Returns magnitude of the quaternion"""
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        """Normalizes quaternion"""
        norm = self.magnitude()
        if norm == 0:
            # Prevent divison by zero
            self.w, self.x, self.y, self.z = 1.0, 0.0, 0.0, 0.0
            return
        self.w /= norm
        self.x /= norm
        self.y /= norm
        self.z /= norm

    def rotate_vector(self, vector: np.ndarray):
        """Rotates the given vector by this Quaternion."""
        vector_as_q = Quaternion(0.0, vector[0], vector[1], vector[2])
        rotated = self * vector_as_q * self.conjugate()

        return np.array([rotated.x, rotated.y, rotated.z], dtype=float)
