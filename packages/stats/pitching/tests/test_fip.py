import json
import unittest
from pathlib import Path

from ..fip import PitchingConstants, fip, load_pitching_constants, xfip


class TestPitchingFIP(unittest.TestCase):
    def test_constants_file_contract(self):
        constants_path = Path(__file__).resolve().parents[1] / "cfip_2026.json"
        payload = json.loads(constants_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["year"], 2026)
        self.assertIn("c_fip", payload)
        self.assertIn("league_hr_per_fb", payload)

    def test_load_constants(self):
        constants = load_pitching_constants(2026)
        self.assertIsInstance(constants, PitchingConstants)
        self.assertAlmostEqual(constants.c_fip, 3.10)
        self.assertAlmostEqual(constants.league_hr_per_fb, 0.12)

    def test_fip_formula(self):
        constants = PitchingConstants(c_fip=3.10, league_hr_per_fb=0.12)
        value = fip(
            home_runs=20,
            walks=30,
            hit_by_pitch=5,
            strikeouts=150,
            innings_pitched=180.0,
            constants=constants,
        )
        self.assertAlmostEqual(value, 3.4611111111, places=6)

    def test_xfip_uses_expected_hr(self):
        constants = PitchingConstants(c_fip=3.10, league_hr_per_fb=0.12)
        value = xfip(
            fly_balls=200,
            walks=30,
            hit_by_pitch=5,
            strikeouts=150,
            innings_pitched=180.0,
            constants=constants,
        )
        self.assertAlmostEqual(value, 3.75, places=6)

    def test_zero_denominator_guards(self):
        constants = PitchingConstants(c_fip=3.10, league_hr_per_fb=0.12)
        self.assertEqual(
            fip(
                home_runs=0,
                walks=0,
                hit_by_pitch=0,
                strikeouts=0,
                innings_pitched=0.0,
                constants=constants,
            ),
            0.0,
        )
        self.assertEqual(
            xfip(
                fly_balls=0,
                walks=0,
                hit_by_pitch=0,
                strikeouts=0,
                innings_pitched=0.0,
                constants=constants,
            ),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
