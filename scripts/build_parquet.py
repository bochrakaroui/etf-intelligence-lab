#!/usr/bin/env python3
"""Materialize compact Parquet snapshots from the generated CSV fixtures."""

from __future__ import annotations

from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "data" / "snapshots"


def sql_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace("'", "''")


def main() -> None:
    csv_files = sorted(SNAPSHOTS.glob("*/etf_snapshot.csv"))
    if not csv_files:
        raise SystemExit("No generated CSV snapshots found. Run scripts/generate_demo_dataset.py first.")
    connection = duckdb.connect(":memory:")
    for source in csv_files:
        target = source.with_suffix(".parquet")
        connection.execute(
            f"COPY (SELECT * FROM read_csv_auto('{sql_path(source)}', header=true, union_by_name=true, nullstr=['','NOT_AVAILABLE'])) "
            f"TO '{sql_path(target)}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
        print(f"Wrote {target.relative_to(ROOT)}")
    connection.close()


if __name__ == "__main__":
    main()
