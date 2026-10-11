import httpx

from database.types import Currency
from .exceptions import CurrencyConversionError

BASE_CURRENCY = Currency.USD
CURRENCY_EXCHANGE_URL = "https://api.frankfurter.dev/v2/rates"

def convert_currency(amount: int, currency: Currency) -> int:
    """
    Converts from BASE_CURRENCY into `currency` using the latest exchange rate.

    :paramter amount: in the smallest unit of the currency (e.g. cents)
    :raises CurrencyConversionError:
    """
    if currency == BASE_CURRENCY:
        return amount

    try:
        response = httpx.get(
            CURRENCY_EXCHANGE_URL,
            params={"base": BASE_CURRENCY.upper(), "quotes": currency.upper()},
        )
        response.raise_for_status()
        rate = response.json()[0]["rate"]
    except (httpx.HTTPError, KeyError, IndexError):
        raise CurrencyConversionError(f"Failed to get exchange rate for {currency}")

    return round(amount * rate)