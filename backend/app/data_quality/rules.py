from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

CURRENCIES = {"EUR", "USD", "GBP", "CHF", "SEK", "NOK", "DKK", "JPY", "CAD", "AUD"}
ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")


def valid_isin_format(value: str | None) -> bool:
    return bool(value and ISIN_RE.fullmatch(value.upper()))


def valid_isin_checksum(value: str | None) -> bool:
    if not valid_isin_format(value):
        return False
    expanded = "".join(str(ord(char) - 55) if char.isalpha() else char for char in value.upper())
    total = 0
    parity = len(expanded) % 2
    for index, char in enumerate(expanded):
        digit = int(char)
        if index % 2 == parity:
            digit *= 2
        total += digit // 10 + digit % 10
    return total % 10 == 0


def parse_date(value: Any) -> date | None:
    if value in (None, "", "NOT_AVAILABLE"):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def quality_score(etf: dict[str, Any], today: date | None = None) -> tuple[int, dict[str, int]]:
    today = today or date.today()
    identifier = 100 if valid_isin_checksum(etf.get("isin")) and etf.get("name") else 45
    aum = 100 if etf.get("aum_millions") not in (None, 0) and etf.get("aum_currency") else 60 if etf.get("aum_millions") else 20
    listings = 100 if etf.get("listing_count", 0) > 0 and etf.get("exchanges") else 30
    snapshot = parse_date(etf.get("snapshot_date"))
    age = (today - snapshot).days if snapshot else 999
    freshness = 100 if age <= 7 else 80 if age <= 30 else 50 if age <= 90 else 20
    currencies = set(etf.get("trading_currencies") or [])
    consistency = 100 if all(currency in CURRENCIES for currency in currencies) else 60
    source_confidence = 96 if etf.get("provider") and snapshot else 65
    dimensions = {
        "identifier": identifier,
        "aum": aum,
        "listings": listings,
        "freshness": freshness,
        "consistency": consistency,
        "source_confidence": source_confidence,
    }
    weights = {"identifier": 0.25, "aum": 0.2, "listings": 0.15, "freshness": 0.15, "consistency": 0.15, "source_confidence": 0.1}
    return round(sum(dimensions[key] * weights[key] for key in dimensions)), dimensions


def validate_listing(row: dict[str, Any], today: date | None = None) -> list[dict[str, str]]:
    today = today or date.today()
    failures: list[dict[str, str]] = []
    isin = str(row.get("isin") or "")
    if not valid_isin_checksum(isin):
        failures.append({"field": "isin", "rule": "valid_isin", "message": "ISIN format or checksum is invalid."})
    aum = row.get("aum_millions")
    if aum is not None:
        try:
            if float(aum) < 0:
                failures.append({"field": "aum_millions", "rule": "non_negative", "message": "AUM cannot be negative."})
        except (TypeError, ValueError):
            failures.append({"field": "aum_millions", "rule": "numeric", "message": "AUM must be numeric."})
    if row.get("trading_currency") not in CURRENCIES:
        failures.append({"field": "trading_currency", "rule": "iso_currency", "message": "Trading currency is not in the supported ISO currency set."})
    listing_date = parse_date(row.get("listing_date"))
    if row.get("listing_date") and listing_date is None:
        failures.append({"field": "listing_date", "rule": "iso_date", "message": "Listing date is not a valid ISO date."})
    elif listing_date and listing_date > today:
        failures.append({"field": "listing_date", "rule": "not_future", "message": "Listing date is in the future."})
    return failures
