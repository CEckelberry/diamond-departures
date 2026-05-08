import json
from typing import Any, cast

from apps.ingest.app.config import IngestSettings
from apps.ingest.app.job import run_once
from apps.ingest.app.mlb_client import MLBResponse


class FakeProvider:
    def __init__(self):
        self.calls: list[object] = []

    def fetch_schedule(self):
        self.calls.append('schedule')
        return MLBResponse(
            status_code=200,
            payload={
                'dates': [
                    {
                        'games': [
                            {
                                'gamePk': 662001,
                                'status': {'abstractGameState': 'Live', 'codedGameState': 'I'},
                            }
                        ]
                    }
                ]
            },
            headers={},
        )

    def fetch_game_changes(self, updated_since: str):
        self.calls.append(('changes', updated_since))
        return MLBResponse(status_code=200, payload={'games': [{'gamePk': 662001}]}, headers={})

    def fetch_live_game_feed(self, game_pk: int):
        self.calls.append(('feed', game_pk))
        return MLBResponse(
            status_code=200,
            payload={
                'gamePk': game_pk,
                'liveData': {
                    'plays': {
                        'allPlays': [
                            {
                                'atBatIndex': 1,
                                'result': {'eventType': 'single'},
                                'matchup': {'batter': {'id': 660271}},
                            }
                        ]
                    }
                },
            },
            headers={},
        )


class FailingChangesProvider(FakeProvider):
    def fetch_game_changes(self, updated_since: str):
        self.calls.append(('changes', updated_since))
        raise RuntimeError('changes endpoint timeout')


class MultiLiveProvider(FakeProvider):
    def fetch_schedule(self):
        self.calls.append('schedule')
        return MLBResponse(
            status_code=200,
            payload={
                'dates': [
                    {
                        'games': [
                            {
                                'gamePk': 662001,
                                'status': {'abstractGameState': 'Live', 'codedGameState': 'I'},
                            },
                            {
                                'gamePk': 662002,
                                'status': {'abstractGameState': 'Live', 'codedGameState': 'I'},
                            },
                        ]
                    }
                ]
            },
            headers={},
        )


class FakeStore:
    def session_factory(self):
        return {'connected': True}


def _settings(
    checkpoint_path: str,
    scanner_mode: str,
    reconcile_every_n_scans: int = 10,
) -> IngestSettings:
    return IngestSettings(
        mlb_api_url='http://mock:8090',
        database_url='sqlite:///./diamond_departures.db',
        log_level='INFO',
        environment='development',
        request_timeout_seconds=10,
        max_http_retries=2,
        retry_backoff_seconds=0.1,
        provider_source='mlb_stats',
        live_scanner_mode=scanner_mode,
        game_changes_lookback_seconds=30,
        scanner_checkpoint_path=checkpoint_path,
        reconcile_every_n_scans=reconcile_every_n_scans,
    )


def test_run_once_wires_provider_and_store(monkeypatch, tmp_path):
    settings = _settings(str(tmp_path / 'checkpoint.json'), 'schedule')
    fake_provider = FakeProvider()
    fake_store = FakeStore()

    monkeypatch.setattr('apps.ingest.app.job.load_settings', lambda: settings)
    monkeypatch.setattr('apps.ingest.app.job.build_provider', lambda _settings: fake_provider)
    monkeypatch.setattr('apps.ingest.app.job.init_store', lambda _: fake_store)

    result = run_once()

    assert result['status'] == 'ok'
    assert result['schedule_status'] == 200
    assert result['games_scanned'] == [662001]
    assert ('feed', 662001) in fake_provider.calls
    delta = cast(dict[str, Any], result['delta_payload'])
    assert delta['changed_player_ids'] == [660271]
    assert ('hitters', 'wRC+') in delta['affected_views']


def test_run_once_changes_mode_uses_checkpoint_cursor(monkeypatch, tmp_path):
    checkpoint_path = tmp_path / 'checkpoint.json'
    checkpoint_path.write_text(
        json.dumps(
            {
                'updated_since': '2026-05-08T11:00:00Z',
                'last_success_at': None,
                'consecutive_failures': 0,
                'scan_count': 1,
            }
        ),
        encoding='utf-8',
    )

    settings = _settings(str(checkpoint_path), 'changes')
    fake_provider = FakeProvider()
    fake_store = FakeStore()

    monkeypatch.setattr('apps.ingest.app.job.load_settings', lambda: settings)
    monkeypatch.setattr('apps.ingest.app.job.build_provider', lambda _settings: fake_provider)
    monkeypatch.setattr('apps.ingest.app.job.init_store', lambda _: fake_store)

    result = run_once(updated_since=None)

    assert result['status'] == 'ok'
    assert result['scanner_mode'] == 'changes'
    assert ('changes', '2026-05-08T11:00:00Z') in fake_provider.calls
    assert result['changed_games'] == [662001]
    assert result['scanner_scan_count'] == 2
    assert result['reconcile_triggered'] is False
    assert result['checkpoint_saved'] is True


def test_run_once_changes_mode_failure_increments_checkpoint_failures(monkeypatch, tmp_path):
    checkpoint_path = tmp_path / 'checkpoint.json'
    checkpoint_path.write_text(
        json.dumps(
            {
                'updated_since': '2026-05-08T11:00:00Z',
                'last_success_at': '2026-05-08T10:59:30Z',
                'consecutive_failures': 1,
                'scan_count': 3,
            }
        ),
        encoding='utf-8',
    )

    settings = _settings(str(checkpoint_path), 'changes')
    fake_provider = FailingChangesProvider()
    fake_store = FakeStore()

    monkeypatch.setattr('apps.ingest.app.job.load_settings', lambda: settings)
    monkeypatch.setattr('apps.ingest.app.job.build_provider', lambda _settings: fake_provider)
    monkeypatch.setattr('apps.ingest.app.job.init_store', lambda _: fake_store)

    result = run_once()

    assert result['status'] == 'degraded'
    assert result['scanner_mode'] == 'changes'
    assert result['changed_games'] == []
    assert result['games_scanned'] == []
    assert result['checkpoint_saved'] is True
    delta = cast(dict[str, Any], result['delta_payload'])
    assert delta['changed_player_ids'] == []
    assert delta['affected_views'] == []
    assert 'timeout' in str(result['error'])

    updated = json.loads(checkpoint_path.read_text(encoding='utf-8'))
    assert updated['updated_since'] == '2026-05-08T11:00:00Z'
    assert updated['consecutive_failures'] == 2
    assert updated['scan_count'] == 4


def test_run_once_triggers_reconcile_sweep_every_n_scans(monkeypatch, tmp_path):
    checkpoint_path = tmp_path / 'checkpoint.json'
    checkpoint_path.write_text(
        json.dumps(
            {
                'updated_since': '2026-05-08T11:00:00Z',
                'last_success_at': '2026-05-08T11:00:10Z',
                'consecutive_failures': 0,
                'scan_count': 1,
            }
        ),
        encoding='utf-8',
    )

    settings = _settings(str(checkpoint_path), 'changes', reconcile_every_n_scans=2)
    fake_provider = MultiLiveProvider()
    fake_store = FakeStore()

    monkeypatch.setattr('apps.ingest.app.job.load_settings', lambda: settings)
    monkeypatch.setattr('apps.ingest.app.job.build_provider', lambda _settings: fake_provider)
    monkeypatch.setattr('apps.ingest.app.job.init_store', lambda _: fake_store)

    result = run_once()

    assert result['status'] == 'ok'
    assert result['scanner_scan_count'] == 2
    assert result['reconcile_triggered'] is True
    assert result['reconcile_games_count'] == 2
    assert result['games_scanned'] == [662001, 662002]
