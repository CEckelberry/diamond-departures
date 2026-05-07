"""ERA+ formula from STATS.md."""


def era_plus(pitcher_era: float, league_era: float, park_factor: float) -> float:
    """ERA+ formula: `100 * (lgERA / ERA) * PF`."""
    if pitcher_era == 0 or league_era == 0:
        return 0.0
    return 100 * (league_era / pitcher_era) * park_factor
