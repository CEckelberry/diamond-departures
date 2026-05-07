"""Qualification helpers for defensive stat stability tags."""


def defensive_sample_tag(innings_played: float, threshold: float = 1000.0) -> str | None:
    """Return `noisy` when innings are below the defensive sample threshold."""

    return "noisy" if innings_played < threshold else None
