import unittest

from ..siera import siera


class TestSIERA(unittest.TestCase):
    def test_siera_formula(self):
        value = siera(
            strikeouts=200,
            walks=50,
            plate_appearances=750,
            ground_balls=300,
            fly_balls=200,
        )
        self.assertAlmostEqual(value, 3.1066177778, places=6)

    def test_zero_guards(self):
        self.assertEqual(
            siera(
                strikeouts=0,
                walks=0,
                plate_appearances=0,
                ground_balls=0,
                fly_balls=0,
            ),
            0.0,
        )
        self.assertEqual(
            siera(
                strikeouts=0,
                walks=0,
                plate_appearances=10,
                ground_balls=0,
                fly_balls=0,
            ),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
