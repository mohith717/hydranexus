import unittest

from detector import detect_possible_leak


class TestLeakDetector(unittest.TestCase):

    def test_normal_usage(self):
        self.assertFalse(
            detect_possible_leak([0.2, 0.3, 0.1, 0.4])
        )

    def test_sustained_high_flow(self):
        self.assertTrue(
            detect_possible_leak([0.2, 1.4, 1.5, 1.6])
        )

    def test_brief_spike(self):
        self.assertFalse(
            detect_possible_leak([0.2, 1.8, 0.2, 0.3])
        )

    def test_reading_equal_to_threshold(self):
        self.assertFalse(
            detect_possible_leak([1.0, 1.0, 1.0])
        )

    def test_custom_threshold(self):
        self.assertTrue(
            detect_possible_leak(
                [1.5, 1.6],
                threshold=1.0,
                consecutive=2,
            )
        )

    def test_negative_reading_rejected(self):
        with self.assertRaises(ValueError):
            detect_possible_leak([0.2, -1.0])

    def test_invalid_consecutive_count(self):
        with self.assertRaises(ValueError):
            detect_possible_leak([1.5], consecutive=0)

    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):
            detect_possible_leak([0.5], threshold=-1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)