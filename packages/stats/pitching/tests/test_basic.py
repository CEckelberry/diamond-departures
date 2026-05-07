import unittest

from ..basic import bb_per_nine, era, k_minus_bb_rate, k_per_nine, whip


class TestPitchingBasic(unittest.TestCase):
    def test_core_rate_formulas(self):
        self.assertAlmostEqual(era(earned_runs=25, innings_pitched=60.0), 3.75)
        self.assertAlmostEqual(whip(walks=20, hits_allowed=40, innings_pitched=60.0), 1.0)
        self.assertAlmostEqual(k_per_nine(strikeouts=90, innings_pitched=60.0), 13.5)
        self.assertAlmostEqual(bb_per_nine(walks=20, innings_pitched=60.0), 3.0)
        self.assertAlmostEqual(k_minus_bb_rate(strikeouts=90, walks=20, batters_faced=250), 0.28)

    def test_zero_denominator_guards(self):
        self.assertEqual(era(earned_runs=0, innings_pitched=0.0), 0.0)
        self.assertEqual(whip(walks=0, hits_allowed=0, innings_pitched=0.0), 0.0)
        self.assertEqual(k_per_nine(strikeouts=0, innings_pitched=0.0), 0.0)
        self.assertEqual(bb_per_nine(walks=0, innings_pitched=0.0), 0.0)
        self.assertEqual(k_minus_bb_rate(strikeouts=0, walks=0, batters_faced=0), 0.0)


if __name__ == "__main__":
    unittest.main()
