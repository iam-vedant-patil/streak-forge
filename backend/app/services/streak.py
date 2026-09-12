from datetime import date, timedelta


def calculate_current_streak(completion_dates: list[date]) -> int:
    if not completion_dates:
        return 0

    completed_dates = set(completion_dates)
    today = date.today()

    if today not in completed_dates:
        return 0

    streak = 0
    current_date = today

    while current_date in completed_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak
