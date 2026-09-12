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


def calculate_longest_streak(completion_dates: list[date]) -> int:
    if not completion_dates:
        return 0

    completed_dates = sorted(set(completion_dates))

    longest_streak = 1
    current_streak = 1

    for index in range(1, len(completed_dates)):
        previous_date = completed_dates[index - 1]
        current_date = completed_dates[index]

        if current_date == previous_date + timedelta(days=1):
            current_streak += 1
        else:
            current_streak = 1

        longest_streak = max(longest_streak, current_streak)

    return longest_streak
