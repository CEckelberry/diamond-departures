import json
from pathlib import Path

from apps.ingest.app.config import IngestSettings
from apps.ingest.app.runner import run_loop


def _settings(tmp_path: Path) -> IngestSettings:
    return IngestSettings(
        mlb_api_url='http://mock:8090',
        database_url='sqlite:///./diamond_departures.db',
        log_level='INFO',
        environment='development',
        request_timeout_seconds=10,
        max_http_retries=2,
        retry_backoff_seconds=0.1,
        provider_source='mlb_stats',
        live_scanner_mode='changes',
        game_changes_lookback_seconds=30,
        scanner_checkpoint_path=str(tmp_path / 'checkpoint.json'),
        reconcile_every_n_scans=10,
        scan_interval_live_seconds=11,
        scan_interval_idle_seconds=47,
        scanner_report_path=str(tmp_path / 'scanner-report.json'),
        season_refresh_live_seconds=60,
        season_refresh_idle_seconds=3600,
        current_season=2026,
    )


def test_run_loop_uses_live_and_idle_sleep_cadence(tmp_path):
    sleeps: list[float] = []
    calls: list[set[str] | None] = []

    results = [
        {'status': 'ok', 'live_games': [1], 'snapshot': {'a'}, 'changed_games_count': 1},
        {'status': 'ok', 'live_games': [], 'snapshot': {'b'}, 'changed_games_count': 0},
        {'status': 'ok', 'live_games': [2], 'snapshot': {'c'}, 'changed_games_count': 1},
    ]

    def fake_run_once(*, previous_snapshot=None):
        calls.append(previous_snapshot)
        return results.pop(0)

    run_loop(
        max_iterations=3,
        settings=_settings(tmp_path),
        run_once_fn=fake_run_once,
        sleep_fn=sleeps.append,
    )

    assert calls == [None, {'a'}, {'b'}]
    assert sleeps == [11.0, 47.0]


def test_run_loop_writes_report_each_iteration(tmp_path):
    report_path = tmp_path / 'scanner-report.json'

    run_loop(
        max_iterations=1,
        settings=_settings(tmp_path),
        run_once_fn=lambda previous_snapshot=None: {
            'status': 'ok',
            'scanner_mode': 'changes',
            'live_games': [662001],
            'changed_games_count': 1,
            'event_count': 2,
            'update_count': 2,
            'scanner_scan_count': 4,
            'reconcile_triggered': False,
            'reconcile_games_count': 0,
            'snapshot': {'x'},
            'error': None,
        },
        sleep_fn=lambda _seconds: None,
    )

    payload = json.loads(report_path.read_text(encoding='utf-8'))
    assert payload['iteration'] == 1
    assert payload['status'] == 'ok'
    assert payload['live_games_count'] == 1
    assert payload['changed_games_count'] == 1
    assert payload['scanner_scan_count'] == 4


def test_season_refresh_called_when_due(tmp_path):
    """run_loop calls season refresh when interval has elapsed."""
    from unittest.mock import MagicMock, patch
    from datetime import UTC, datetime, timedelta

    settings = IngestSettings(
        mlb_api_url="http://mock",
        database_url="postgresql://x",
        log_level="INFO",
        environment="test",
        request_timeout_seconds=5,
        max_http_retries=0,
        retry_backoff_seconds=0,
        provider_source="mlb_stats",
        live_scanner_mode="all",
        game_changes_lookback_seconds=30,
        scanner_checkpoint_path="/tmp/cp.json",
        reconcile_every_n_scans=10,
        scan_interval_live_seconds=15,
        scan_interval_idle_seconds=60,
        scanner_report_path="/tmp/report.json",
        season_refresh_live_seconds=60,
        season_refresh_idle_seconds=3600,
        current_season=2026,
    )

    mock_run_once = MagicMock(return_value={"status": "ok", "live_games": [], "snapshot": set()})
    mock_refresh = MagicMock()
    mock_sleep = MagicMock()

    with patch("apps.ingest.app.runner.SeasonStatsRefresher") as MockRefresher:
        MockRefresher.return_value.refresh = mock_refresh
        run_loop(
            max_iterations=2,
            settings=settings,
            run_once_fn=mock_run_once,
            sleep_fn=mock_sleep,
        )

    assert mock_refresh.called
