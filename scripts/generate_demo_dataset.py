#!/usr/bin/env python3
"""Generate deterministic, explicitly synthetic ETF snapshots for the portfolio app."""

from __future__ import annotations

import csv
import json
import math
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "snapshots"
SEED = 20260828

ISSUERS = [
    ("Atlas Index", "Atlas Data Feed"), ("Northstar Asset Management", "Northstar Public Data"),
    ("Helix Funds", "Helix Market Files"), ("Meridian ETFs", "Meridian Data Service"),
    ("Aperture Index", "Aperture Public Feed"), ("Cedar Capital", "Cedar Fund Data"),
    ("Quarry Investments", "Quarry Product Feed"), ("Vela Asset Management", "Vela Fund Files"),
]
ASSETS = {
    "Equity": [("Global Large Cap", "Global Developed 1000", "Core"), ("US Equity", "US Large Cap 500", "Core"), ("European Equity", "Europe 600", "Core"), ("Emerging Markets", "Emerging Markets Broad", "Core"), ("Technology", "Global Technology Leaders", "Thematic"), ("Climate Transition", "Global Climate Transition", "ESG")],
    "Fixed Income": [("Global Aggregate Bond", "Global Aggregate Bond", "Core"), ("Euro Government Bond", "Euro Sovereign 7-10Y", "Duration"), ("Corporate Bond", "Global Corporate Bond", "Income"), ("Short Duration", "EUR Corporate 1-3Y", "Defensive")],
    "Commodity": [("Broad Commodities", "Diversified Commodity", "Broad"), ("Gold", "Physical Gold Reference", "Single commodity")],
    "Multi-Asset": [("Balanced", "Global 60/40", "Allocation"), ("Defensive Allocation", "Global 30/70", "Allocation")],
}
EXCHANGES = [
    ("London Stock Exchange", "XLON", "GB", ["GBP", "USD"]),
    ("Deutsche Börse Xetra", "XETR", "DE", ["EUR"]),
    ("Euronext Paris", "XPAR", "FR", ["EUR"]),
    ("Borsa Italiana", "XMIL", "IT", ["EUR"]),
    ("SIX Swiss Exchange", "XSWX", "CH", ["CHF", "USD"]),
    ("Euronext Amsterdam", "XAMS", "NL", ["EUR"]),
    ("Bolsa de Madrid", "XMAD", "ES", ["EUR"]),
]
FIELDS = ["isin", "name", "issuer", "fund_family", "asset_class", "category", "strategy", "benchmark", "domicile", "fund_currency", "aum_millions", "aum_currency", "inception_date", "age_years", "replication_method", "distribution_policy", "ter", "exchange", "exchange_code", "ticker", "trading_currency", "listing_date", "country", "provider", "snapshot_date", "retrieved_at"]


def isin_for(serial: int) -> str:
    body = f"IE{serial:09d}"
    expanded = "".join(str(ord(char) - 55) if char.isalpha() else char for char in body)
    for check in range(10):
        candidate = expanded + str(check)
        total, parity = 0, len(candidate) % 2
        for index, char in enumerate(candidate):
            digit = int(char) * (2 if index % 2 == parity else 1)
            total += digit // 10 + digit % 10
        if total % 10 == 0:
            return body + str(check)
    raise AssertionError("Unable to create ISIN")


def build_funds(count: int = 240) -> list[dict]:
    rng = random.Random(SEED)
    funds = []
    styles = [item for asset, rows in ASSETS.items() for item in rows for _ in range(1 if asset != "Equity" else 2)]
    for index in range(count):
        issuer, provider = ISSUERS[index % len(ISSUERS)]
        asset_class = list(ASSETS)[index % len(ASSETS)] if index % 5 else "Equity"
        category, benchmark, strategy = rng.choice(ASSETS[asset_class])
        inception = date(2006, 1, 1) + timedelta(days=rng.randint(0, 7300))
        currency = rng.choices(["EUR", "USD", "GBP", "CHF"], [52, 28, 13, 7])[0]
        suffix = rng.choice(["UCITS ETF", "Index ETF", "Screened UCITS ETF", "Enhanced ETF"])
        name = f"{issuer.split()[0]} {category} {suffix}"
        base = round(math.exp(rng.uniform(math.log(18), math.log(18000))), 2)
        funds.append({
            "isin": isin_for(100000000 + index), "name": name, "issuer": issuer, "fund_family": issuer,
            "asset_class": asset_class, "category": category, "strategy": strategy, "benchmark": benchmark,
            "domicile": rng.choice(["IE", "LU"]), "fund_currency": currency, "aum_millions": base,
            "aum_currency": currency, "inception_date": inception.isoformat(),
            "replication_method": rng.choices(["Physical", "Sampling", "Synthetic"], [62, 25, 13])[0],
            "distribution_policy": rng.choice(["Accumulating", "Distributing"]),
            "ter": round(rng.uniform(0.05, 0.75), 2), "provider": provider,
        })
    funds[7]["aum_millions"] = 0
    funds[23]["aum_millions"] = None
    funds[117]["ter"] = 1.95
    return funds


def rows_for_snapshot(funds: list[dict], snapshot: date, version: int) -> list[dict]:
    rng = random.Random(SEED + version)
    active = funds[: 225 + version * 7]
    rows = []
    for index, fund in enumerate(active):
        listing_total = 1 + rng.choices([0, 1, 2, 3], [22, 42, 27, 9])[0]
        if index == 31 and version == 2:
            listing_total = 7
        for exchange_index in rng.sample(range(len(EXCHANGES)), min(listing_total, len(EXCHANGES))):
            exchange, code, country, currencies = EXCHANGES[exchange_index]
            listing_date = date.fromisoformat(fund["inception_date"]) + timedelta(days=rng.randint(5, 900))
            growth = 1 + version * rng.uniform(0.008, 0.045)
            aum = round(fund["aum_millions"] * growth, 2) if fund["aum_millions"] is not None else None
            row = {**fund, "aum_millions": aum, "age_years": round((snapshot - date.fromisoformat(fund["inception_date"])).days / 365.25, 1), "exchange": exchange, "exchange_code": code, "ticker": f"{fund['issuer'][:2].upper()}{index:03d}{exchange_index}", "trading_currency": rng.choice(currencies), "listing_date": listing_date.isoformat(), "country": country, "snapshot_date": snapshot.isoformat(), "retrieved_at": datetime.combine(snapshot, datetime.min.time(), tzinfo=timezone.utc).replace(hour=6, minute=30).isoformat()}
            rows.append(row)
    if version == 2:
        rows[17]["listing_date"] = (snapshot + timedelta(days=21)).isoformat()
        rows.append(dict(rows[42]))
    return rows


def main() -> None:
    funds = build_funds()
    snapshots = [date(2026, 8, 14), date(2026, 8, 21), date(2026, 8, 28)]
    for version, snapshot in enumerate(snapshots):
        directory = OUTPUT / snapshot.isoformat()
        directory.mkdir(parents=True, exist_ok=True)
        rows = rows_for_snapshot(funds, snapshot, version)
        path = directory / "etf_snapshot.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        metadata = {"mode": "DEMO", "synthetic": True, "snapshot_date": snapshot.isoformat(), "records": len(rows), "unique_isins": len({row['isin'] for row in rows}), "notice": "Generated data for demonstration only. Not investment data or advice."}
        (directory / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Generated {len(snapshots)} synthetic snapshots in {OUTPUT}")


if __name__ == "__main__":
    main()
