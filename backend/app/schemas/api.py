from typing import Any

from pydantic import BaseModel, Field


class QualityBreakdown(BaseModel):
    identifier: int
    aum: int
    listings: int
    freshness: int
    consistency: int
    source_confidence: int


class ETFSummary(BaseModel):
    isin: str
    name: str
    issuer: str
    asset_class: str | None = None
    category: str | None = None
    aum_millions: float | None = None
    aum_currency: str | None = None
    ter: float | None = None
    age_years: float | None = None
    listing_count: int
    exchanges: list[str] = Field(default_factory=list)
    trading_currencies: list[str] = Field(default_factory=list)
    snapshot_date: str
    quality_score: int
    quality: QualityBreakdown


class PaginatedETFs(BaseModel):
    items: list[ETFSummary]
    page: int
    page_size: int
    total: int
    pages: int


class SimilarityContribution(BaseModel):
    signal: str
    contribution: float
    detail: str


class SimilarETF(BaseModel):
    etf: ETFSummary
    similarity_score: float
    explanation: list[SimilarityContribution]


class Anomaly(BaseModel):
    id: str
    isin: str | None = None
    provider: str | None = None
    anomaly_type: str
    severity: str
    title: str
    explanation: str
    observed: str
    expected: str
    snapshot_date: str
    method: str


class ProviderQuality(BaseModel):
    provider: str
    reliability_score: int
    completeness: float
    freshness: float
    consistency: float
    uniqueness: float
    validity: float
    anomaly_rate: float
    record_count: int
    status: str


class CopilotResponse(BaseModel):
    mode: str = "local"
    intent: str
    answer: str
    data: Any
    suggested_follow_ups: list[str] = Field(default_factory=list)
