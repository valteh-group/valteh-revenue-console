from datetime import date


def current_month_key(today: date | None = None) -> str:
    today = today or date.today()
    return today.strftime("%Y-%m")


def month_key(value: date) -> str:
    return value.strftime("%Y-%m")


def month_range(start_month: str, end_month: str) -> list[str]:
    start_year, start_month_number = (int(part) for part in start_month.split("-"))
    end_year, end_month_number = (int(part) for part in end_month.split("-"))
    current = date(start_year, start_month_number, 1)
    end = date(end_year, end_month_number, 1)
    months = []
    while current <= end:
        months.append(month_key(current))
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months
