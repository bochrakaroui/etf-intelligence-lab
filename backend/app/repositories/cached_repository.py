from __future__ import annotations

from pathlib import Path
from typing import Any

from app.repositories.parquet_repository import ParquetETFRepository


class CachedParquetETFRepository(ParquetETFRepository):
    """Small instance-scoped read-through cache for immutable demo snapshots."""

    def __init__(self, data_dir: Path, database_path: Path):
        super().__init__(data_dir, database_path)
        self._all_etfs: list[dict[str, Any]] | None = None
        self._listings: list[dict[str, Any]] | None = None
        self._dimensions: dict[str, list[str]] | None = None
        self._etf_cache: dict[str, dict[str, Any] | None] = {}
        self._query_cache: dict[tuple[Any, ...], tuple[list[dict[str, Any]], int]] = {}

    def all_etfs(self) -> list[dict[str, Any]]:
        if self._all_etfs is None:
            self._all_etfs = super().all_etfs()
        return self._all_etfs

    def listings(self) -> list[dict[str, Any]]:
        if self._listings is None:
            self._listings = super().listings()
        return self._listings

    def dimensions(self) -> dict[str, list[str]]:
        if self._dimensions is None:
            self._dimensions = super().dimensions()
        return self._dimensions

    def get_etf(self, isin: str) -> dict[str, Any] | None:
        key = isin.upper()
        if key not in self._etf_cache:
            self._etf_cache[key] = super().get_etf(key)
        return self._etf_cache[key]

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
        key = (search, issuer, exchange, currency, asset_class, provider, min_aum, max_aum, sort, order, page, page_size)
        if key not in self._query_cache:
            self._query_cache[key] = super().list_etfs(
                search=search, issuer=issuer, exchange=exchange, currency=currency,
                asset_class=asset_class, provider=provider, min_aum=min_aum,
                max_aum=max_aum, sort=sort, order=order, page=page, page_size=page_size,
            )
        return self._query_cache[key]
