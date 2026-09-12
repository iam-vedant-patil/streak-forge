from datetime import date, timedelta

from backend.app.services.streak import (
    calculate_current_streak,
    calculate_longest_streak,
)


def test_current_streak_empty():
    assert calculate_current_streak([]) == 0


def test_current_streak_today_only():
    today = date.today()

    assert calculate_current_streak([today]) == 1


def test_current_streak_consecutive_days():
    today = date.today()

    completion_dates = [
        today - timedelta(days=2),
        today - timedelta(days=1),
        today,
    ]

    assert calculate_current_streak(completion_dates) == 3


def test_current_streak_break():
    today = date.today()

    completion_dates = [
        today - timedelta(days=2),
        today,
    ]

    assert calculate_current_streak(completion_dates) == 1


def test_longest_streak_empty():
    assert calculate_longest_streak([]) == 0


def test_longest_streak_single_day():
    assert calculate_longest_streak([date(2026, 9, 10)]) == 1


def test_longest_streak_consecutive_days():
    completion_dates = [
        date(2026, 9, 8),
        date(2026, 9, 9),
        date(2026, 9, 10),
    ]

    assert calculate_longest_streak(completion_dates) == 3


def test_longest_streak_with_gap():
    completion_dates = [
        date(2026, 9, 1),
        date(2026, 9, 2),
        date(2026, 9, 3),
        date(2026, 9, 7),
        date(2026, 9, 8),
    ]

    assert calculate_longest_streak(completion_dates) == 3


def test_longest_streak_current_shorter_than_longest():
    today = date.today()

    completion_dates = [
        today - timedelta(days=5),
        today - timedelta(days=4),
        today - timedelta(days=3),
        today - timedelta(days=1),
        today,
    ]

    assert calculate_longest_streak(completion_dates) == 3
