from __future__ import annotations

import math
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.analytics.stats import automated_insights, dataset_stats
from app.ml.anomalies import detect_anomalies, provider_quality
from app.ml.similarity import SimilarityEngine
from app.repositories.etf_repository import ETFRepository
from app.services.history import snapshot_diff

router = APIRouter()


def repository(request: Request) -> ETFRepository:
    return request.app.state.repository


@router.get("/health")
def health(repo: ETFRepository = Depends(repository)):
    return {"status": "healthy", "service": "etf-intelligence-lab", "mode": "demo", "snapshot": repo.latest_snapshot()}


@router.get("/api/stats")
def stats(repo: ETFRepository = Depends(repository)):
    etfs, listings = repo.all_etfs(), repo.listings()
    anomalies = detect_anomalies(etfs, listings)
    providers = provider_quality(etfs, anomalies)
    result = dataset_stats(etfs, listings, anomalies)
    result["insights"] = automated_insights(result, providers)
    result["providers"] = providers[:6]
    result["recent_anomalies"] = anomalies[:8]
    return result


@router.get("/api/etfs")
def etfs(
    search: str | None = None, issuer: str | None = None, exchange: str | None = None,
    currency: str | None = None, asset_class: str | None = None, provider: str | None = None,
    min_aum: float | None = None, max_aum: float | None = None, sort: str = "aum_millions",
    order: str = "desc", page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100),
    repo: ETFRepository = Depends(repository),
):
    items, total = repo.list_etfs(search=search, issuer=issuer, exchange=exchange, currency=currency, asset_class=asset_class, provider=provider, min_aum=min_aum, max_aum=max_aum, sort=sort, order=order, page=page, page_size=page_size)
    return {"items": items, "page": page, "page_size": page_size, "total": total, "pages": math.ceil(total / page_size)}


@router.get("/api/dimensions")
def dimensions(repo: ETFRepository = Depends(repository)):
    return repo.dimensions()


@router.get("/api/etfs/{isin}")
def etf(isin: str, repo: ETFRepository = Depends(repository)):
    item = repo.get_etf(isin)
    if not item:
        raise HTTPException(404, "ETF not found")
    return item


@router.get("/api/etfs/{isin}/similar")
def similar_etfs(isin: str, limit: int = Query(8, ge=1, le=20), repo: ETFRepository = Depends(repository)):
    if not repo.get_etf(isin):
        raise HTTPException(404, "ETF not found")
    return {"isin": isin.upper(), "method": "weighted_tfidf_structured_cosine", "weights": SimilarityEngine.__module__ and __import__('app.ml.similarity', fromlist=['WEIGHTS']).WEIGHTS, "items": SimilarityEngine(repo.all_etfs()).similar(isin, limit)}


@router.get("/api/etfs/{isin}/anomalies")
def etf_anomalies(isin: str, repo: ETFRepository = Depends(repository)):
    return [item for item in detect_anomalies(repo.all_etfs(), repo.listings()) if item.get("isin") == isin.upper()]


@router.get("/api/anomalies")
def anomalies(severity: str | None = None, provider: str | None = None, repo: ETFRepository = Depends(repository)):
    items = detect_anomalies(repo.all_etfs(), repo.listings())
    return [item for item in items if (not severity or item["severity"] == severity) and (not provider or item.get("provider") == provider)]


@router.get("/api/providers")
def providers(repo: ETFRepository = Depends(repository)):
    etf_rows, listing_rows = repo.all_etfs(), repo.listings()
    return provider_quality(etf_rows, detect_anomalies(etf_rows, listing_rows))


@router.get("/api/providers/{provider_name}/quality")
def provider(provider_name: str, repo: ETFRepository = Depends(repository)):
    result = next((item for item in providers(repo) if item["provider"].casefold() == provider_name.casefold()), None)
    if not result:
        raise HTTPException(404, "Provider not found")
    result["formula"] = "30% completeness + 25% freshness + 15% consistency + 10% uniqueness + 15% validity + 5% inverse anomaly rate"
    return result


@router.get("/api/compare")
def compare(isins: str = Query(..., description="Comma-separated list of 2–5 ISINs"), repo: ETFRepository = Depends(repository)):
    values = list(dict.fromkeys(item.strip().upper() for item in isins.split(",") if item.strip()))
    if not 2 <= len(values) <= 5:
        raise HTTPException(422, "Provide between 2 and 5 distinct ISINs")
    items = [repo.get_etf(value) for value in values]
    if any(item is None for item in items):
        raise HTTPException(404, "One or more ETFs were not found")
    typed = [item for item in items if item]
    largest, smallest = max(typed, key=lambda x: x.get("aum_millions") or 0), min(typed, key=lambda x: x.get("aum_millions") or 0)
    ratio = (largest.get("aum_millions") or 0) / max(smallest.get("aum_millions") or 1, 1)
    summary = f"{largest['name']} has approximately {ratio:.1f}× the reported AUM of {smallest['name']} and trades on {largest['listing_count']} versus {smallest['listing_count']} listings."
    return {"items": typed, "summary": summary}


@router.get("/api/history")
def history(repo: ETFRepository = Depends(repository)):
    dates = repo.snapshot_dates()
    return {"available": len(dates) > 1, "snapshots": dates, "latest": dates[-1]}


@router.get("/api/history/diff")
def history_diff(from_date: str, to_date: str, repo: ETFRepository = Depends(repository)):
    dates = repo.snapshot_dates()
    if from_date not in dates or to_date not in dates:
        raise HTTPException(404, "Snapshot not found")
    return snapshot_diff(repo.snapshot_rows(from_date), repo.snapshot_rows(to_date), from_date, to_date)


@router.get("/api/network/{isin}")
def network(isin: str, threshold: float = Query(55, ge=0, le=100), repo: ETFRepository = Depends(repository)):
    center = repo.get_etf(isin)
    if not center:
        raise HTTPException(404, "ETF not found")
    matches = [item for item in SimilarityEngine(repo.all_etfs()).similar(isin, 18) if item["similarity_score"] >= threshold]
    return {"nodes": [{"id": center["isin"], "label": center["name"], "issuer": center["issuer"], "aum": center.get("aum_millions"), "central": True}, *[{"id": item["etf"]["isin"], "label": item["etf"]["name"], "issuer": item["etf"]["issuer"], "aum": item["etf"].get("aum_millions"), "central": False} for item in matches]], "edges": [{"source": center["isin"], "target": item["etf"]["isin"], "score": item["similarity_score"], "explanation": item["explanation"][:3]} for item in matches]}


@router.get("/api/lineage/{isin}")
def lineage(isin: str, repo: ETFRepository = Depends(repository)):
    item = repo.get_etf(isin)
    if not item:
        raise HTTPException(404, "ETF not found")
    return {"isin": isin.upper(), "nodes": [{"id": "source", "label": "Synthetic provider snapshot", "status": "verified"}, {"id": "raw", "label": "Allowlisted CSV record", "status": "accepted"}, {"id": "normalize", "label": "Polars normalization", "status": "passed"}, {"id": "dedupe", "label": "Listing-key deduplication", "status": "passed"}, {"id": "entity", "label": "ETF entity", "status": "ready"}, {"id": "analytics", "label": "Analytics + similarity", "status": "ready"}], "provenance": item["provenance"]}


@router.post("/api/copilot")
def copilot(payload: dict, repo: ETFRepository = Depends(repository)):
    question = str(payload.get("question") or "").strip()
    lower = question.casefold()
    etf_rows, listing_rows = repo.all_etfs(), repo.listings()
    if "largest" in lower:
        match = re.search(r"(\d+)", lower)
        limit = min(int(match.group(1)) if match else 5, 20)
        data = sorted(etf_rows, key=lambda item: item.get("aum_millions") or 0, reverse=True)[:limit]
        answer, intent = f"Here are the {limit} largest ETFs by reported AUM in the demo snapshot.", "get_largest_etfs"
    elif "provider" in lower and any(word in lower for word in ("weak", "quality", "complete", "reliable")):
        data = provider_quality(etf_rows, detect_anomalies(etf_rows, listing_rows))
        answer, intent = f"{data[-1]['provider']} currently has the weakest reliability score at {data[-1]['reliability_score']}/100.", "get_provider_quality"
    elif "anomal" in lower:
        data = detect_anomalies(etf_rows, listing_rows)[:10]
        answer, intent = f"I found {len(detect_anomalies(etf_rows, listing_rows))} explained anomalies; these are the highest-priority results.", "get_anomalies"
    else:
        isin_match = re.search(r"[A-Z]{2}[A-Z0-9]{9}[0-9]", question.upper())
        if isin_match and "similar" in lower:
            data = SimilarityEngine(etf_rows).similar(isin_match.group(0), 5)
            answer, intent = "These are the closest ETFs using the transparent weighted similarity model.", "find_similar"
        else:
            items, _ = repo.list_etfs(search=question, page_size=8)
            data = items
            answer, intent = f"I found {len(items)} matching ETFs in the local demo dataset.", "search_etfs"
    return {"mode": "local", "intent": intent, "answer": answer, "data": data, "suggested_follow_ups": ["Show the five largest ETFs", "Which provider has the weakest completeness?", "Show recent anomalies"]}
