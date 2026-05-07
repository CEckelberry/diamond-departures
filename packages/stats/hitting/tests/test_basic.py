import unittest

from ..basic import avg, babip, iso, obp, ops, slg


class TestHittingBasic(unittest.TestCase):
    def test_avg(self):
        self.assertAlmostEqual(avg(h=150, ab=500), 0.3)
        self.assertEqual(avg(h=0, ab=0), 0.0)

    def test_obp_formula_sample(self):
        self.assertAlmostEqual(obp(h=150, bb=60, hbp=5, ab=500, sf=5), 215 / 570)

    def test_slg_formula_sample(self):
        self.assertAlmostEqual(slg(singles=95, doubles=30, triples=5, home_runs=20, ab=500), 0.5)

    def test_ops_formula_sample(self):
        self.assertAlmostEqual(ops(obp_value=0.37719298245614036, slg_value=0.5), 0.8771929824561404)

    def test_iso_formula_sample(self):
        self.assertAlmostEqual(iso(slg_value=0.5, avg_value=0.3), 0.2)

    def test_babip_formula_sample(self):
        self.assertAlmostEqual(babip(h=150, home_runs=20, ab=500, strikeouts=100, sf=5), 130 / 385)

    def test_zero_denominator_guards(self):
        self.assertEqual(avg(h=0, ab=0), 0.0)
        self.assertEqual(obp(h=0, bb=0, hbp=0, ab=0, sf=0), 0.0)
        self.assertEqual(slg(singles=0, doubles=0, triples=0, home_runs=0, ab=0), 0.0)
        self.assertEqual(babip(h=0, home_runs=0, ab=0, strikeouts=0, sf=0), 0.0)


if __name__ == "__main__":
    unittest.main()
