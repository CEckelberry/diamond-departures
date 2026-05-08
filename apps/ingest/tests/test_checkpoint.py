import json

from apps.ingest.app.checkpoint import load_checkpoint, save_checkpoint


def test_load_checkpoint_defaults_when_missing(tmp_path):
    path = tmp_path / 'checkpoint.json'

    checkpoint = load_checkpoint(str(path))

    assert checkpoint['updated_since'] is None
    assert checkpoint['last_success_at'] is None
    assert checkpoint['consecutive_failures'] == 0


def test_save_and_load_checkpoint_roundtrip(tmp_path):
    path = tmp_path / 'checkpoint.json'
    payload = {
        'updated_since': '2026-05-08T11:00:00Z',
        'last_success_at': '2026-05-08T11:00:10Z',
        'consecutive_failures': 2,
    }

    save_checkpoint(str(path), payload)
    loaded = load_checkpoint(str(path))

    assert loaded == payload


def test_save_checkpoint_atomic_overwrite(tmp_path):
    path = tmp_path / 'checkpoint.json'

    save_checkpoint(
        str(path),
        {'updated_since': '2026-05-08T11:00:00Z', 'last_success_at': None, 'consecutive_failures': 0},
    )
    save_checkpoint(
        str(path),
        {'updated_since': '2026-05-08T11:00:30Z', 'last_success_at': '2026-05-08T11:00:31Z', 'consecutive_failures': 1},
    )

    loaded = json.loads(path.read_text(encoding='utf-8'))
    assert loaded['updated_since'] == '2026-05-08T11:00:30Z'
    assert loaded['last_success_at'] == '2026-05-08T11:00:31Z'
    assert loaded['consecutive_failures'] == 1
