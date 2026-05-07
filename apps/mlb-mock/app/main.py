from __future__ import annotations

import argparse
import json
import time
from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

DATA_DIR = Path(__file__).resolve().parent / "data"


class MockState:
    def __init__(self, replay_speed: float) -> None:
        self.replay_speed = replay_speed
        self.boot_time = time.time()
        self.schedule = self._load_json("schedule_today.json")
        self.feed_template = self._load_json("game_feed_template.json")
        self.people_stats = self._load_json("people_stats_660271.json")
        self.roster = self._load_json("roster_147.json")

    @staticmethod
    def _load_json(name: str) -> dict[str, Any]:
        with (DATA_DIR / name).open("r", encoding="utf-8") as f:
            return json.load(f)

    def feed_for_game(self, game_pk: int) -> dict[str, Any]:
        template = deepcopy(self.feed_template)
        template["gamePk"] = game_pk

        elapsed = max(0.0, time.time() - self.boot_time)
        progress = int(elapsed * self.replay_speed)

        inning = (progress % 9) + 1
        inning_state = "Top" if progress % 2 == 0 else "Bottom"
        at_bat_index = progress
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        template.setdefault("metaData", {})["timeStamp"] = stamp
        template.setdefault("liveData", {}).setdefault("linescore", {})["currentInning"] = inning
        template["liveData"]["linescore"]["inningState"] = inning_state
        template.setdefault("liveData", {}).setdefault("plays", {}).setdefault("currentPlay", {})[
            "atBatIndex"
        ] = at_bat_index
        return template


class MLBMockHandler(BaseHTTPRequestHandler):
    state: MockState

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/v1/schedule":
            self._json(200, self.state.schedule)
            return

        if path.startswith("/api/v1/game/") and path.endswith("/feed/live"):
            parts = path.strip("/").split("/")
            if len(parts) != 6:
                self._json(404, {"message": "not found"})
                return
            try:
                game_pk = int(parts[3])
            except ValueError:
                self._json(400, {"message": "invalid game id"})
                return
            self._json(200, self.state.feed_for_game(game_pk))
            return

        if path.startswith("/api/v1/people/") and path.endswith("/stats"):
            groups = [g.strip().lower() for g in ",".join(query.get("group", [])).split(",") if g.strip()]
            payload = deepcopy(self.state.people_stats)
            if groups:
                payload["stats"] = [
                    item
                    for item in payload.get("stats", [])
                    if str(item.get("group", {}).get("displayName", "")).lower() in groups
                ]
            self._json(200, payload)
            return

        if path.startswith("/api/v1/teams/") and path.endswith("/roster"):
            self._json(200, self.state.roster)
            return

        self._json(404, {"message": "not found"})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MLB mock service")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=8090, type=int)
    parser.add_argument("--replay-speed", default=300.0, type=float)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    MLBMockHandler.state = MockState(replay_speed=args.replay_speed)
    server = ThreadingHTTPServer((args.host, args.port), MLBMockHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
