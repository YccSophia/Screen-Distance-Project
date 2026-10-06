import unittest
from monitor import classify, light_round_trip_seconds


class MonitorTests(unittest.TestCase):
    def test_boundaries(self):
        for cm, expected in [(24.99, 'BLOCK'), (25, 'WARN'), (30, 'WARN'), (30.01, 'NORMAL')]:
            with self.subTest(cm=cm):
                self.assertEqual(classify(cm).state, expected)

    def test_invalid_measurements(self):
        for cm in [0, -1, float('nan'), float('inf'), -float('inf')]:
            with self.subTest(cm=cm), self.assertRaises(ValueError):
                classify(cm)

    def test_round_trip_units(self):
        self.assertAlmostEqual(light_round_trip_seconds(30), 2e-9, delta=1e-20)


if __name__ == '__main__':
    unittest.main()
