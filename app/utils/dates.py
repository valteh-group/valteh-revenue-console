from datetime import date


def current_month_key(today: date | None = None) -> str:
    today = today or date.today()
    return today.strftime("%Y-%m")


def available_months() -> list[str]:
    return ["2026-04", "2026-05", "2026-06"]
