"""Basic hitting stat formulas from STATS.md."""


def avg(h: int, ab: int) -> float:
    """Batting average: H / AB."""
    return 0.0 if ab == 0 else h / ab


def obp(h: int, bb: int, hbp: int, ab: int, sf: int) -> float:
    """On-base percentage: (H + BB + HBP) / (AB + BB + HBP + SF)."""
    denom = ab + bb + hbp + sf
    return 0.0 if denom == 0 else (h + bb + hbp) / denom


def slg(singles: int, doubles: int, triples: int, home_runs: int, ab: int) -> float:
    """Slugging percentage: TB / AB where TB = 1B + 2*2B + 3*3B + 4*HR."""
    if ab == 0:
        return 0.0
    total_bases = singles + (2 * doubles) + (3 * triples) + (4 * home_runs)
    return total_bases / ab


def ops(obp_value: float, slg_value: float) -> float:
    """On-base plus slugging: OBP + SLG."""
    return obp_value + slg_value


def iso(slg_value: float, avg_value: float) -> float:
    """Isolated power: SLG - AVG."""
    return slg_value - avg_value


def babip(h: int, home_runs: int, ab: int, strikeouts: int, sf: int) -> float:
    """Batting average on balls in play: (H - HR) / (AB - K - HR + SF)."""
    denom = ab - strikeouts - home_runs + sf
    return 0.0 if denom == 0 else (h - home_runs) / denom
