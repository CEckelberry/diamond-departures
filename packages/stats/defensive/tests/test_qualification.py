import unittest

from ..qualification import defensive_sample_tag


class TestDefensiveQualification(unittest.TestCase):
    def test_sub_threshold_tagged_noisy(self):
        self.assertEqual(defensive_sample_tag(innings_played=999.0), "noisy")
        self.assertEqual(defensive_sample_tag(innings_played=450.5), "noisy")

    def test_threshold_or_above_not_noisy(self):
        self.assertIsNone(defensive_sample_tag(innings_played=1000.0))
        self.assertIsNone(defensive_sample_tag(innings_played=1305.2))


if __name__ == "__main__":
    unittest.main()
