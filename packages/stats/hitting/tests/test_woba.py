import json
import unittest
from pathlib import Path

from ..woba import WOBAWeights, load_woba_weights, woba


class TestWOBA(unittest.TestCase):
    def test_load_woba_weights_2026(self):
        weights = load_woba_weights(2026)
        self.assertIsInstance(weights, WOBAWeights)
        self.assertAlmostEqual(weights.walk, 0.69)
        self.assertAlmostEqual(weights.hit_by_pitch, 0.72)
        self.assertAlmostEqual(weights.single, 0.89)
        self.assertAlmostEqual(weights.double, 1.27)
        self.assertAlmostEqual(weights.triple, 1.62)
        self.assertAlmostEqual(weights.home_run, 2.10)

    def test_weights_file_shape_contract(self):
        weights_path = Path(__file__).resolve().parents[1] / "woba_weights_2026.json"
        payload = json.loads(weights_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["year"], 2026)
        self.assertIn("weights", payload)
        for key in ["bb", "hbp", "1b", "2b", "3b", "hr"]:
            self.assertIn(key, payload["weights"])

    def test_woba_formula_with_ibb_guard(self):
        weights = WOBAWeights(0.69, 0.72, 0.89, 1.27, 1.62, 2.10)
        value = woba(
            singles=100,
            doubles=20,
            triples=5,
            home_runs=20,
            walks=50,
            intentional_walks=5,
            hit_by_pitch=10,
            at_bats=500,
            sacrifice_flies=5,
            weights=weights,
        )
        self.assertAlmostEqual(value, 206.2 / 560, places=6)

    def test_zero_denominator_returns_zero(self):
        weights = WOBAWeights(0.69, 0.72, 0.89, 1.27, 1.62, 2.10)
        value = woba(
            singles=0,
            doubles=0,
            triples=0,
            home_runs=0,
            walks=0,
            intentional_walks=0,
            hit_by_pitch=0,
            at_bats=0,
            sacrifice_flies=0,
            weights=weights,
        )
        self.assertEqual(value, 0.0)


if __name__ == "__main__":
    unittest.main()
