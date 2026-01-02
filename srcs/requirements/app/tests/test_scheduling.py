import datetime as dt

from tools.scheduling import parse_interval_seconds, compute_initial_delay, load_schedule_config


def test_parse_interval_seconds_variants():
    assert parse_interval_seconds("10s") == 10
    assert parse_interval_seconds("2m") == 120
    assert parse_interval_seconds("1h") == 3600
    assert parse_interval_seconds("1d") == 86400
    assert parse_interval_seconds(30) == 30


def test_compute_initial_delay_future_and_past():
    now = dt.datetime(2024, 1, 1, 12, 0, 0)
    # start_time plus tard dans la journée
    delay = compute_initial_delay("13:00", now=now)
    assert delay == 3600
    # start_time déjà passé -> lendemain
    delay_next_day = compute_initial_delay("11:00", now=now)
    assert delay_next_day == 23 * 3600


def test_compute_initial_delay_with_timezone_keeps_expected_gap():
    now = dt.datetime(2024, 1, 1, 12, 0, 0)
    delay = compute_initial_delay("13:00", now=now, timezone="Europe/Paris")
    assert delay == 3600


def test_compute_initial_delay_same_minute_is_zero():
    now = dt.datetime(2024, 1, 1, 20, 0, 0)
    delay = compute_initial_delay("20:00", now=now)
    assert delay == 0


def test_load_schedule_config_defaults():
    cfg = load_schedule_config(None)
    assert cfg.interval_seconds > 0
    assert cfg.retry_on_failure is True
    assert cfg.max_retries == 3
