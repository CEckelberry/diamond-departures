from __future__ import annotations

from .mlb_client import MLBApiClient


class SavantClient:
    """Thin wrapper around Baseball Savant's leaderboard endpoint.

    Uses the same MLBApiClient retry/backoff pattern, different base URL.
    The Savant leaderboard returns a JSON object with a top-level key
    that varies by endpoint; we normalise the response to a list of dicts
    with snake_case keys matching our stat_name conventions.
    """

    def __init__(
        self,
        base_url: str = "https://baseballsavant.mlb.com",
        timeout_seconds: int = 15,
        max_retries: int = 3,
    ) -> None:
        self._mlb_client = MLBApiClient(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

    def fetch_statcast(self, *, year: int) -> list[dict]:
        """Return list of Statcast batting metrics for all qualified hitters.

        Each dict has keys: player_id (int), barrel_pct, hard_hit_pct,
        exit_velocity, xwoba, xba (all float).
        """
        path = (
            f"/leaderboard/expected_statistics"
            f"?type=batter&year={year}&position=&team=&min=q"
        )
        response = self._mlb_client.get_json(path)
        raw = response.payload

        players = raw.get("players") or raw.get("leaderboard") or []
        if not players:
            return []

        result = []
        for item in players:
            try:
                result.append({
                    "player_id": int(item["player_id"]),
                    "barrel_pct": float(item.get("barrel_batted_rate") or 0),
                    "hard_hit_pct": float(item.get("hard_hit_percent") or 0),
                    "exit_velocity": float(item.get("avg_hit_speed") or 0),
                    "xwoba": float(item.get("xwoba") or 0),
                    "xba": float(item.get("xba") or 0),
                })
            except (KeyError, TypeError, ValueError):
                continue
        return result
