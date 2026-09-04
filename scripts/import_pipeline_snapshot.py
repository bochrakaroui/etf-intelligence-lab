#!/usr/bin/env python3
"""Sanitize an exported aggregate snapshot into the standalone public schema."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl


PUBLIC_INPUTS = {"ticker", "exchange_code", "name", "isin", "listing_date", "trading_currency", "asset_class", "ter", "aum", "total_aum", "aum_currency", "exchange", "issuer", "aum_date"}


def sanitize(source: Path, destination: Path, snapshot_date: str) -> None:
    frame = pl.read_csv(source, null_values=["", "NOT_AVAILABLE"], infer_schema_length=10000)
    selected = [column for column in frame.columns if column in PUBLIC_INPUTS]
    frame = frame.select(selected)
    defaults = {
        "fund_family": pl.col("issuer") if "issuer" in frame.columns else pl.lit(None), "category": pl.lit(None), "strategy": pl.lit(None),
        "benchmark": pl.lit(None), "domicile": pl.lit(None), "fund_currency": pl.lit(None), "inception_date": pl.lit(None),
        "age_years": pl.lit(None), "replication_method": pl.lit(None), "distribution_policy": pl.lit(None),
        "country": pl.col("exchange_code") if "exchange_code" in frame.columns else pl.lit(None), "provider": pl.lit("Sanitized public snapshot"),
        "snapshot_date": pl.lit(snapshot_date), "retrieved_at": pl.lit(datetime.now(timezone.utc).isoformat()),
    }
    if "aum" in frame.columns:
        frame = frame.rename({"aum": "aum_millions"})
    for name, expression in defaults.items():
        if name not in frame.columns:
            frame = frame.with_columns(expression.alias(name))
    if "aum_currency" not in frame.columns:
        frame = frame.with_columns(pl.lit(None).alias("aum_currency"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.write_csv(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--snapshot-date", default=date.today().isoformat())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path("data/snapshots") / args.snapshot_date / "etf_snapshot.csv"
    sanitize(args.source, output, args.snapshot_date)
    print(f"Wrote sanitized snapshot to {output}")


if __name__ == "__main__":
    main()
