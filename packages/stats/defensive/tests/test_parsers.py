import unittest

from ..parsers import parse_defensive_metrics


class TestDefensiveParsers(unittest.TestCase):
    def test_parse_metrics_from_mlb_and_statcast(self):
        mlb_payload = {
            "stats": {
                "fielding": {
                    "drs": 14,
                    "uzr": 6.2,
                    "uzr_150": 5.8,
                }
            }
        }
        statcast_payload = {"fieldingRunValue": {"oaa": 9}}

        metrics = parse_defensive_metrics(mlb_payload=mlb_payload, statcast_payload=statcast_payload)

        self.assertEqual(metrics["drs"], 14)
        self.assertAlmostEqual(metrics["uzr"], 6.2)
        self.assertAlmostEqual(metrics["uzr_150"], 5.8)
        self.assertEqual(metrics["oaa"], 9)

    def test_parse_with_uzr_per_game_needing_150_normalization(self):
        mlb_payload = {
            "stats": {
                "fielding": {
                    "drs": 8,
                    "uzr": 0.045,
                    "uzr_is_per_game": True,
                    "games": 120,
                }
            }
        }
        statcast_payload = {"fieldingRunValue": {"oaa": -1}}

        metrics = parse_defensive_metrics(mlb_payload=mlb_payload, statcast_payload=statcast_payload)

        self.assertAlmostEqual(metrics["uzr_150"], 6.75, places=6)


if __name__ == "__main__":
    unittest.main()
