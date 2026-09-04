from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import duckdb

from app.data_quality.rules import quality_score


class ETFRepository:
    def __init__(self, data_dir: Path, database_path: Path):
        self.data_dir = Path(data_dir)
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.database_path))

    def bootstrap(self) -> None:
        snapshot_glob = str((self.data_dir / "*" / "etf_snapshot.csv").resolve()).replace("\\", "/")
        if not list(self.data_dir.glob("*/etf_snapshot.csv")):
            raise RuntimeError(f"No demo snapshots found in {self.data_dir}. Run scripts/generate_demo_dataset.py first.")
        with self.connect() as connection:
            connection.execute(
                f"CREATE OR REPLACE TABLE listing_snapshots AS SELECT * FROM read_csv_auto('{snapshot_glob}', header=true, union_by_name=true, nullstr=['','NOT_AVAILABLE'])"
            )
            connection.execute("CREATE OR REPLACE TABLE listings AS SELECT * FROM listing_snapshots WHERE snapshot_date=(SELECT max(snapshot_date) FROM listing_snapshots)")
            connection.execute(
                """
                CREATE OR REPLACE TABLE etfs AS
                SELECT isin, any_value(name) AS name, any_value(issuer) AS issuer,
                       any_value(fund_family) AS fund_family, any_value(asset_class) AS asset_class,
                       any_value(category) AS category, any_value(strategy) AS strategy,
                       any_value(benchmark) AS benchmark, any_value(domicile) AS domicile,
                       any_value(fund_currency) AS fund_currency, max(aum_millions) AS aum_millions,
                       any_value(aum_currency) AS aum_currency, min(inception_date) AS inception_date,
                       max(age_years) AS age_years, any_value(replication_method) AS replication_method,
                       any_value(distribution_policy) AS distribution_policy, max(ter) AS ter,
                       count(DISTINCT exchange_code || ':' || ticker) AS listing_count,
                       list(DISTINCT exchange ORDER BY exchange) AS exchanges,
                       list(DISTINCT ticker ORDER BY ticker) AS tickers,
                       list(DISTINCT trading_currency ORDER BY trading_currency) AS trading_currencies,
                       any_value(provider) AS provider, max(snapshot_date) AS snapshot_date,
                       max(retrieved_at) AS retrieved_at
                FROM listings GROUP BY isin
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS etfs_isin_idx ON etfs(isin)")
            connection.execute("CREATE INDEX IF NOT EXISTS listings_isin_idx ON listings(isin)")

    @staticmethod
    def _records(cursor: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
        columns = [item[0] for item in cursor.description]
        records = []
        for row in cursor.fetchall():
            record = dict(zip(columns, row, strict=True))
            for key, value in list(record.items()):
                if hasattr(value, "isoformat"):
                    record[key] = value.isoformat()
                elif isinstance(value, float) and math.isnan(value):
                    record[key] = None
            records.append(record)
        return records

    def latest_snapshot(self) -> str:
        with self.connect() as connection:
            return str(connection.execute("SELECT max(snapshot_date) FROM listing_snapshots").fetchone()[0])

    def snapshot_dates(self) -> list[str]:
        with self.connect() as connection:
            return [str(row[0]) for row in connection.execute("SELECT DISTINCT snapshot_date FROM listing_snapshots ORDER BY snapshot_date").fetchall()]

    def list_etfs(
        self,
        *,
        search: str | None = None,
        issuer: str | None = None,
        exchange: str | None = None,
        currency: str | None = None,
        asset_class: str | None = None,
        provider: str | None = None,
        min_aum: float | None = None,
        max_aum: float | None = None,
        sort: str = "aum_millions",
        order: str = "desc",
        page: int = 1,
        page_size: int = 25,
    ) -> tuple[list[dict[str, Any]], int]:
        clauses = ["1=1"]
        params: list[Any] = []
        if search:
            clauses.append("(name ILIKE ? OR isin ILIKE ? OR issuer ILIKE ? OR benchmark ILIKE ?)")
            needle = f"%{search}%"
            params.extend([needle] * 4)
        for column, value in [("issuer", issuer), ("asset_class", asset_class), ("provider", provider)]:
            if value:
                clauses.append(f"{column} = ?")
                params.append(value)
        if exchange:
            clauses.append("list_contains(exchanges, ?)")
            params.append(exchange)
        if currency:
            clauses.append("list_contains(trading_currencies, ?)")
            params.append(currency)
        if min_aum is not None:
            clauses.append("aum_millions >= ?")
            params.append(min_aum)
        if max_aum is not None:
            clauses.append("aum_millions <= ?")
            params.append(max_aum)
        allowed_sorts = {"name", "issuer", "aum_millions", "ter", "age_years", "listing_count", "snapshot_date"}
        sort = sort if sort in allowed_sorts else "aum_millions"
        direction = "ASC" if order.lower() == "asc" else "DESC"
        where = " AND ".join(clauses)
        with self.connect() as connection:
            total = connection.execute(f"SELECT count(*) FROM etfs WHERE {where}", params).fetchone()[0]
            query_params = [*params, page_size, (page - 1) * page_size]
            cursor = connection.execute(f"SELECT * FROM etfs WHERE {where} ORDER BY {sort} {direction} NULLS LAST LIMIT ? OFFSET ?", query_params)
            return [self.enrich_quality(row) for row in self._records(cursor)], total

    def get_etf(self, isin: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            records = self._records(connection.execute("SELECT * FROM etfs WHERE isin=?", [isin.upper()]))
            if not records:
                return None
            etf = self.enrich_quality(records[0])
            etf["listings"] = self._records(connection.execute("SELECT exchange, exchange_code, ticker, trading_currency, listing_date, country, snapshot_date FROM listings WHERE isin=? ORDER BY exchange, ticker", [isin.upper()]))
            etf["provenance"] = {
                "provider": etf.get("provider"),
                "snapshot_date": etf.get("snapshot_date"),
                "retrieved_at": etf.get("retrieved_at"),
                "normalization_status": "normalized",
                "validation_status": "passed" if etf["quality_score"] >= 70 else "review",
                "source": "sanitized synthetic snapshot",
            }
            return etf

    def all_etfs(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            return [self.enrich_quality(row) for row in self._records(connection.execute("SELECT * FROM etfs ORDER BY isin"))]

    def listings(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            return self._records(connection.execute("SELECT * FROM listings"))

    def snapshot_rows(self, snapshot_date: str) -> list[dict[str, Any]]:
        with self.connect() as connection:
            return self._records(connection.execute("SELECT * FROM listing_snapshots WHERE snapshot_date=?", [snapshot_date]))

    @staticmethod
    def enrich_quality(row: dict[str, Any]) -> dict[str, Any]:
        score, breakdown = quality_score(row)
        row["quality_score"] = score
        row["quality"] = breakdown
        return row

    def dimensions(self) -> dict[str, list[str]]:
        with self.connect() as connection:
            result: dict[str, list[str]] = {}
            for name, column, table in [
                ("issuers", "issuer", "etfs"), ("asset_classes", "asset_class", "etfs"),
                ("providers", "provider", "etfs"), ("exchanges", "exchange", "listings"),
                ("currencies", "trading_currency", "listings"),
            ]:
                result[name] = [str(row[0]) for row in connection.execute(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}").fetchall()]
            return result
