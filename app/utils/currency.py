from decimal import Decimal

BASE_CURRENCY = "MXN"
STATIC_EXCHANGE_RATES_TO_MXN = {
    "MXN": Decimal("1"),
    "USD": Decimal("18"),
}


def convert_to_mxn(value: Decimal | float | int | str, currency: str) -> Decimal:
    currency_code = currency.strip().upper()
    try:
        rate = STATIC_EXCHANGE_RATES_TO_MXN[currency_code]
    except KeyError as exc:
        supported = ", ".join(sorted(STATIC_EXCHANGE_RATES_TO_MXN))
        raise ValueError(
            f"Unsupported currency '{currency}'. Configure an FX rate. Supported currencies: {supported}"
        ) from exc
    return Decimal(str(value)) * rate


def format_mxn(value: Decimal | float | int) -> str:
    return f"${float(value):,.0f} MXN"


def format_percent(value: Decimal | float | int) -> str:
    return f"{float(value) * 100:.1f}%"
