import unittest
from unittest.mock import patch
import reaction_wheel_pd

class TestReactionWheelControl(unittest.TestCase):

    @patch('time.monotonic_ns')
    def test_pd_control_iteration(self, mock_time):
        """Test 1 second iteration of the pd_controller"""

        # Simulate a 1-second passage of time
        start_time = 1_000_000_000  # 1 second in nanoseconds
        next_time = 2_000_000_000   # 2 seconds in nanoseconds
        
        mock_time.return_value = next_time
        
        desired_value = 10.0
        current_value = 8.0
        prev_error = 5.0
        prev_time = start_time
        
        # Expected Calculations:
        # dt = (2.0 - 1.0) = 1.0s
        # error = 10.0 - 8.0 = 2.0
        # p_term = KP * 2.0 = 2.0
        # d_term = KD * (2.0 - 5.0) / 1.0 = -3.0
        
        p_term, d_term, current_time, error = reaction_wheel_pd.reaction_wheel_pd_control(
            desired_value, current_value, prev_error, prev_time
        )
        
        self.assertEqual(error, 2.0)
        self.assertEqual(p_term, 2.0 * reaction_wheel_pd.KP)
        self.assertEqual(d_term, -3.0 * reaction_wheel_pd.KD)
        self.assertEqual(current_time, next_time)

    @patch('time.monotonic_ns')
    def test_zero_error_steady_state(self, mock_time):
        """Test that terms are zero (or expected) when system is at equilibrium."""
        
        mock_time.return_value = 2_000_000_000
        
        p_term, d_term, _, error = reaction_wheel_pd.reaction_wheel_pd_control(
            desired_value=10, 
            current_value=10, 
            prev_error=0, 
            prev_time=1_000_000_000
        )
        
        self.assertEqual(error, 0)
        self.assertEqual(p_term, 0)
        self.assertEqual(d_term, 0)

    @patch('time.monotonic_ns')
    def test_reach_zero_error(self, mock_time):
        """Test that the system reaches zero error in a reasonable time"""
        mock_time.return_value = 1

        desired_value=10
        current_value=8
        prev_error=0
        prev_time=0

        while (mock_time.return_value < 100_000_000_000):
            p_term, d_term, current_time, error = reaction_wheel_pd.reaction_wheel_pd_control(
            desired_value, 
            current_value, 
            prev_error, 
            prev_time
            )

            prev_error = error
            current_value = p_term * reaction_wheel_pd.KP + d_term * reaction_wheel_pd.KD
            prev_time = current_time
            mock_time.return_value += 1
        
        # Error is within 2 decimal places of 0
        self.assertAlmostEqual(error, 0, 2)


if __name__ == '__main__':
    unittest.main()