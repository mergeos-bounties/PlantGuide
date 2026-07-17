from __future__ import annotations

from datetime import date

from typer.testing import CliRunner

from plantguide.care.cards import watering_schedule
from plantguide.cli import app


def test_schedule_returns_reproducible_check_dates() -> None:
    result = watering_schedule(
        "monstera_deliciosa",
        18,
        season="summer",
        climate="temperate",
        as_of=date(2026, 7, 17),
    )

    assert result["interval_days"] == 6
    assert result["next_check_dates"] == ["2026-07-23", "2026-07-29", "2026-08-04"]


def test_larger_pot_and_humid_climate_extend_interval() -> None:
    small_arid = watering_schedule(
        "monstera_deliciosa", 10, climate="arid", as_of=date(2026, 7, 17)
    )
    large_humid = watering_schedule(
        "monstera_deliciosa", 32, climate="humid", as_of=date(2026, 7, 17)
    )

    assert large_humid["interval_days"] > small_arid["interval_days"]


def test_schedule_rejects_unknown_climate() -> None:
    try:
        watering_schedule("monstera_deliciosa", 18, climate="tropical")
    except ValueError as exc:
        assert "climate must be one of" in str(exc)
    else:
        raise AssertionError("unknown climate should be rejected")


def test_schedule_cli_outputs_dates() -> None:
    result = CliRunner().invoke(
        app,
        [
            "care",
            "schedule",
            "--species",
            "monstera_deliciosa",
            "--pot-cm",
            "18",
            "--season",
            "summer",
            "--climate",
            "temperate",
            "--as-of",
            "2026-07-17",
        ],
    )

    assert result.exit_code == 0
    assert '"interval_days": 6' in result.stdout
    assert "2026-07-23" in result.stdout
