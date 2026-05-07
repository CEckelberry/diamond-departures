"""Basic pitching rate stats from STATS.md."""


def era(earned_runs: int, innings_pitched: float) -> float:
    """ERA formula: `(ER * 9) / IP`."""
    return 0.0 if innings_pitched == 0 else (earned_runs * 9) / innings_pitched


def whip(walks: int, hits_allowed: int, innings_pitched: float) -> float:
    """WHIP formula: `(BB + H) / IP`."""
    return 0.0 if innings_pitched == 0 else (walks + hits_allowed) / innings_pitched


def k_per_nine(strikeouts: int, innings_pitched: float) -> float:
    """K/9 formula: `(K * 9) / IP`."""
    return 0.0 if innings_pitched == 0 else (strikeouts * 9) / innings_pitched


def bb_per_nine(walks: int, innings_pitched: float) -> float:
    """BB/9 formula: `(BB * 9) / IP`."""
    return 0.0 if innings_pitched == 0 else (walks * 9) / innings_pitched


def k_minus_bb_rate(strikeouts: int, walks: int, batters_faced: int) -> float:
    """K-BB% formula: `(K - BB) / TBF`."""
    return 0.0 if batters_faced == 0 else (strikeouts - walks) / batters_faced
