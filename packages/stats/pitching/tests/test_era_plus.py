import unittest

from ..era_plus import era_plus


class TestERAPlus(unittest.TestCase):
    def test_era_plus_formula(self):
        value = era_plus(pitcher_era=3.0, league_era=4.2, park_factor=0.98)
        self.assertAlmostEqual(value, 137.2)

    def test_zero_guards(self):
        self.assertEqual(era_plus(pitcher_era=0.0, league_era=4.2, park_factor=1.0), 0.0)
        self.assertEqual(era_plus(pitcher_era=3.0, league_era=0.0, park_factor=1.0), 0.0)


if __name__ == "__main__":
    unittest.main()
