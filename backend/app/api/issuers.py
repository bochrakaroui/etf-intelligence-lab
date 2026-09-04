from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends, Request

from app.repositories.etf_repository import ETFRepository

router = APIRouter()


def repository(request: Request) -> ETFRepository:
    return request.app.state.repository


@router.get("/api/issuers")
def issuers(repo: ETFRepository = Depends(repository)):  # noqa: B008
    grouped: dict[str, dict[str, float | int | str]] = defaultdict(
        lambda: {"issuer": "", "etf_count": 0, "reported_aum_millions": 0.0}
    )
    for item in repo.all_etfs():
        name = str(item["issuer"])
        grouped[name]["issuer"] = name
        grouped[name]["etf_count"] = int(grouped[name]["etf_count"]) + 1
        grouped[name]["reported_aum_millions"] = round(
            float(grouped[name]["reported_aum_millions"]) + float(item.get("aum_millions") or 0), 2
        )
    return sorted(grouped.values(), key=lambda item: float(item["reported_aum_millions"]), reverse=True)

