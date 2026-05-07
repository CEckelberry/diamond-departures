import unittest

from ..wrc import LeagueContext, wrc_plus
from ..woba import WOBAWeights


class TestWRCPlus(unittest.TestCase):
    def test_league_context_required_fields(self):
        context = LeagueContext(
            league_woba=0.320,
            woba_scale=1.25,
            league_runs_per_pa=0.12,
            park_factor=1.0,
        )
        self.assertAlmostEqual(context.league_woba, 0.320)
        self.assertAlmostEqual(context.woba_scale, 1.25)
        self.assertAlmostEqual(context.league_runs_per_pa, 0.12)
        self.assertAlmostEqual(context.park_factor, 1.0)

    def test_wrc_plus_formula_sample(self):
        context = LeagueContext(
            league_woba=0.320,
            woba_scale=1.25,
            league_runs_per_pa=0.12,
            park_factor=1.0,
        )
        weights = WOBAWeights(0.69, 0.72, 0.89, 1.27, 1.62, 2.10)

        value = wrc_plus(
            singles=100,
            doubles=20,
            triples=5,
            home_runs=20,
            walks=50,
            intentional_walks=5,
            hit_by_pitch=10,
            at_bats=500,
            sacrifice_flies=5,
            context=context,
            weights=weights,
        )

        self.assertAlmostEqual(value, 132.14, places=2)

    def test_zero_context_guard(self):
        context = LeagueContext(
            league_woba=0.320,
            woba_scale=0.0,
            league_runs_per_pa=0.0,
            park_factor=1.0,
        )
        weights = WOBAWeights(0.69, 0.72, 0.89, 1.27, 1.62, 2.10)
        value = wrc_plus(
            singles=0,
            doubles=0,
            triples=0,
            home_runs=0,
            walks=0,
            intentional_walks=0,
            hit_by_pitch=0,
            at_bats=0,
            sacrifice_flies=0,
            context=context,
            weights=weights,
        )
        self.assertEqual(value, 0.0)


if __name__ == "__main__":
    unittest.main()
