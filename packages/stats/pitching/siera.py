"""SIERA implementation using deterministic coefficient form."""


def siera(
    strikeouts: int,
    walks: int,
    plate_appearances: int,
    ground_balls: int,
    fly_balls: int,
) -> float:
    """Compute SIERA from K%, BB%, and GB-FB rate with standard coefficients."""

    if plate_appearances == 0 or fly_balls == 0:
        return 0.0

    strikeout_rate = strikeouts / plate_appearances
    walk_rate = walks / plate_appearances
    gb_minus_fb_rate = (ground_balls - fly_balls) / plate_appearances

    return (
        6.145
        - (16.986 * strikeout_rate)
        + (11.434 * walk_rate)
        - (1.858 * gb_minus_fb_rate)
        + (7.653 * strikeout_rate * strikeout_rate)
        + (6.664 * gb_minus_fb_rate * gb_minus_fb_rate)
        + (10.130 * strikeout_rate * gb_minus_fb_rate)
        - (5.195 * walk_rate * gb_minus_fb_rate)
    )
