from pathlib import Path


def test_verify_harness_module_exists() -> None:
    from .. import harness  # noqa: F401


def test_harness_api_contract() -> None:
    from ..harness import VerificationMismatch, run_verification

    assert VerificationMismatch.__name__ == "VerificationMismatch"
    assert callable(run_verification)


def test_tolerance_and_mismatch_reporting_contract() -> None:
    from ..harness import compare_stat

    no_diff = compare_stat(
        player_id=1,
        player_name="Contract Player",
        stat_key="avg",
        expected=0.300,
        actual=0.301,
        tolerance=0.005,
    )
    assert no_diff is None

    mismatch = compare_stat(
        player_id=1,
        player_name="Contract Player",
        stat_key="avg",
        expected=0.300,
        actual=0.310,
        tolerance=0.005,
    )
    assert mismatch is not None
    text = mismatch.to_error_line()
    for token in ["player_id=1", "player_name=Contract Player", "stat=avg", "expected=0.3", "actual=0.31", "pct_diff="]:
        assert token in text


def test_ci_has_verification_hook() -> None:
    workflow = Path(__file__).resolve().parents[4] / ".github" / "workflows" / "ci.yml"
    contents = workflow.read_text(encoding="utf-8")
    assert "packages/stats/verify/tests" in contents
