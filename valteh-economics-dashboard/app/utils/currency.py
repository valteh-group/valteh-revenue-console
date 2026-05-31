from decimal import Decimal


def format_mxn(value: Decimal | float | int) -> str:
    return f"${float(value):,.0f} MXN"


def format_percent(value: Decimal | float | int) -> str:
    return f"{float(value) * 100:.1f}%"
