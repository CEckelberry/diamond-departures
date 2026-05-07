"""Defensive stat parsers for mixed MLB API and Statcast response shapes."""

from __future__ import annotations


def parse_defensive_metrics(mlb_payload: dict, statcast_payload: dict) -> dict:
    """Extract DRS, UZR, UZR/150, and OAA from source payloads."""

    fielding = mlb_payload.get("stats", {}).get("fielding", {})
    drs = fielding.get("drs")
    uzr = fielding.get("uzr")

    if fielding.get("uzr_is_per_game") and uzr is not None:
        uzr_150 = uzr * 150
    else:
        uzr_150 = fielding.get("uzr_150")

    oaa = statcast_payload.get("fieldingRunValue", {}).get("oaa")

    return {
        "drs": drs,
        "uzr": uzr,
        "uzr_150": uzr_150,
        "oaa": oaa,
    }
