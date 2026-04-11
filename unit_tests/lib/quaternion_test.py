import unittest
import math
from quaternion import Quaternion

try:
    import ulab.numpy as np  # For CircuitPython
except ImportError:
    import numpy as np  # For GitHub Actions / PC testing


class QuaternionTest(unittest.TestCase):

    def assertQuaternionAlmostEqual(self, q1, q2, places=6):
        self.assertAlmostEqual(q1.w, q2.w, places=places)
        self.assertAlmostEqual(q1.x, q2.x, places=places)
        self.assertAlmostEqual(q1.y, q2.y, places=places)
        self.assertAlmostEqual(q1.z, q2.z, places=places)

    def test_normalization(self):
        q = Quaternion(1.0, 2.0, 3.0, 4.0)
        q.normalize()

        # Compute the expected magnitude before normalization
        mag = math.sqrt(1**2 + 2**2 + 3**2 + 4**2)  # = sqrt(30)

        # Expected normalized values
        expected = Quaternion(1.0 / mag, 2.0 / mag, 3.0 / mag, 4.0 / mag)

        self.assertQuaternionAlmostEqual(q, expected)
        self.assertAlmostEqual(q.magnitude(), 1.0, places=6)

    def test_conjugate(self):
        q = Quaternion(1, 1, 2, 3)
        qc = q.conjugate()

        # Expected normalized values
        expected = Quaternion(1.0, -1.0, -2.0, -3.0)

        self.assertQuaternionAlmostEqual(qc, expected)

    def test_multiplication(self):
        q1 = Quaternion(1.0, 0.0, 1.0, 0.0)
        q2 = Quaternion(1.0, 0.5, 0.5, 0.75)
        q3 = q1 * q2

        # Expected result from manual multiplication
        expected = Quaternion(0.5, 1.25, 1.5, 0.25)  # w  # x  # y  # z
        self.assertQuaternionAlmostEqual(q3, expected)

    def test_right_multiplication(self):
        q1 = Quaternion(1, 2, 4, 6)
        q2 = Quaternion(3, 6, 12, 18)
        self.assertQuaternionAlmostEqual(3 * q1, q2)

    def test_rotate_vector_identity(self):
        q = Quaternion(1.0, 0.0, 0.0, 0.0)  # Identity rotation
        v = np.array([1.0, 0.0, 0.0])
        rotated = q.rotate_vector(v)
        self.assertAlmostEqual(v[0], 1.0, places=6)
        self.assertAlmostEqual(v[1], 0.0, places=6)
        self.assertAlmostEqual(v[2], 0.0, places=6)

    def test_rotate_vector_90deg_z(self):
        # 90-degree rotation around z-axis
        angle = math.pi / 2
        q = Quaternion(math.cos(angle / 2), 0.0, 0.0, math.sin(angle / 2))
        v = np.array([1.0, 0.0, 0.0])
        rotated = q.rotate_vector(v)
        expected = np.array([0.0, 1.0, 0.0])
        self.assertAlmostEqual(rotated[0], expected[0], places=6)
        self.assertAlmostEqual(rotated[1], expected[1], places=6)
        self.assertAlmostEqual(rotated[2], expected[2], places=6)


if __name__ == "__main__":
    unittest.main()
