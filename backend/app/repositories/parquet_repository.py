from __future__ import annotations

from app.repositories.etf_repository import ETFRepository


class ParquetETFRepository(ETFRepository):
    """DuckDB repository that prefers compact Parquet snapshots over CSV."""

    def bootstrap(self) -> None:
        parquet_files = list(self.data_dir.glob("*/etf_snapshot.parquet"))
        csv_files = list(self.data_dir.glob("*/etf_snapshot.csv"))
        if parquet_files:
            snapshot_glob = str((self.data_dir / "*" / "etf_snapshot.parquet").resolve()).replace("\\", "/")
            source_sql = f"read_parquet('{snapshot_glob}', union_by_name=true)"
        elif csv_files:
            snapshot_glob = str((self.data_dir / "*" / "etf_snapshot.csv").resolve()).replace("\\", "/")
            source_sql = f"read_csv_auto('{snapshot_glob}', header=true, union_by_name=true, nullstr=['','NOT_AVAILABLE'])"
        else:
            raise RuntimeError(f"No demo snapshots found in {self.data_dir}. Run scripts/generate_demo_dataset.py first.")

        with self.connect() as connection:
            connection.execute(f"CREATE OR REPLACE TABLE listing_snapshots AS SELECT * FROM {source_sql}")
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
