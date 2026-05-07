import json
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "http://localhost:8090"


class MLBMockContractTests(unittest.TestCase):
    maxDiff = None

    def _get_json(self, path: str) -> dict:
        url = f"{BASE_URL}{path}"
        req = urllib.request.Request(url, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=3) as response:
                status = response.getcode()
                body = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            self.fail(f"request failed for {url}: {exc}")

        self.assertEqual(status, 200, f"expected HTTP 200 from {url}")

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            self.fail(f"invalid JSON from {url}: {exc}")

        self.assertIsInstance(payload, dict, f"expected top-level object from {url}")
        return payload

    def test_schedule_today_contract(self):
        payload = self._get_json("/api/v1/schedule?date=today")

        for key in ("totalItems", "totalGames", "dates"):
            self.assertIn(key, payload)

        self.assertIsInstance(payload["dates"], list)
        self.assertGreater(len(payload["dates"]), 0, "schedule must include at least one date")

        first_date = payload["dates"][0]
        for key in ("date", "totalGames", "games"):
            self.assertIn(key, first_date)

        self.assertIsInstance(first_date["games"], list)
        self.assertGreater(len(first_date["games"]), 0, "today schedule must include games")

        first_game = first_date["games"][0]
        for key in ("gamePk", "gameDate", "status", "teams"):
            self.assertIn(key, first_game)

        for side in ("away", "home"):
            self.assertIn(side, first_game["teams"])
            self.assertIn("team", first_game["teams"][side])
            self.assertIn("id", first_game["teams"][side]["team"])

    def test_game_feed_contract(self):
        schedule = self._get_json("/api/v1/schedule?date=today")
        game_id = schedule["dates"][0]["games"][0]["gamePk"]

        payload = self._get_json(f"/api/v1/game/{game_id}/feed/live")

        for key in ("gamePk", "gameData", "liveData"):
            self.assertIn(key, payload)

        game_data = payload["gameData"]
        for key in ("status", "teams"):
            self.assertIn(key, game_data)

        status = game_data["status"]
        for key in ("abstractGameState", "detailedState"):
            self.assertIn(key, status)

        live_data = payload["liveData"]
        for key in ("plays", "linescore"):
            self.assertIn(key, live_data)

    def test_people_stats_contract(self):
        query = urllib.parse.urlencode({"group": "hitting,pitching"})
        payload = self._get_json(f"/api/v1/people/660271/stats?{query}")

        self.assertIn("stats", payload)
        self.assertIsInstance(payload["stats"], list)
        self.assertGreater(len(payload["stats"]), 0, "stats array must not be empty")

        groups = {item.get("group", {}).get("displayName") for item in payload["stats"]}
        self.assertTrue(
            {"hitting", "pitching"}.issubset({g.lower() for g in groups if isinstance(g, str)}),
            "expected both hitting and pitching groups in response",
        )

    def test_roster_contract(self):
        payload = self._get_json("/api/v1/teams/147/roster")

        for key in ("roster", "teamId"):
            self.assertIn(key, payload)

        self.assertIsInstance(payload["roster"], list)
        self.assertGreater(len(payload["roster"]), 0, "roster must contain players")

        first_player = payload["roster"][0]
        for key in ("person", "jerseyNumber", "position", "status"):
            self.assertIn(key, first_player)

        self.assertIn("id", first_player["person"])
        self.assertIn("abbreviation", first_player["position"])

    def test_replay_speed_contract(self):
        schedule = self._get_json("/api/v1/schedule?date=today")
        games = schedule["dates"][0]["games"]

        live_games = [
            game
            for game in games
            if str(game.get("status", {}).get("abstractGameState", "")).lower() == "live"
        ]
        self.assertGreater(
            len(live_games),
            0,
            "replay contract requires at least one live game in today's schedule",
        )

        game_id = live_games[0]["gamePk"]
        feed_a = self._get_json(f"/api/v1/game/{game_id}/feed/live")
        time.sleep(1.0)
        feed_b = self._get_json(f"/api/v1/game/{game_id}/feed/live")

        def extract_progress_markers(feed: dict) -> tuple:
            meta = feed.get("metaData", {})
            linescore = feed.get("liveData", {}).get("linescore", {})
            plays = feed.get("liveData", {}).get("plays", {})
            return (
                meta.get("timeStamp"),
                linescore.get("currentInning"),
                linescore.get("inningState"),
                plays.get("currentPlay", {}).get("atBatIndex"),
            )

        marker_a = extract_progress_markers(feed_a)
        marker_b = extract_progress_markers(feed_b)

        self.assertNotEqual(
            marker_a,
            marker_b,
            "expected game feed to advance between rapid polls when mock is run with replay speed",
        )


if __name__ == "__main__":
    unittest.main()
