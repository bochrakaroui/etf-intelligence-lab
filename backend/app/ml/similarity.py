from __future__ import annotations

import math
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

WEIGHTS = {
    "semantic": 0.25,
    "asset_class": 0.20,
    "category": 0.12,
    "benchmark": 0.13,
    "currency": 0.08,
    "issuer": 0.05,
    "exchange": 0.07,
    "aum": 0.07,
    "age": 0.03,
}


def _same(left: Any, right: Any) -> float:
    return 1.0 if left and right and str(left).casefold() == str(right).casefold() else 0.0


def _overlap(left: list[str], right: list[str]) -> float:
    a, b = set(left or []), set(right or [])
    return len(a & b) / len(a | b) if a and b else 0.0


def _numeric_proximity(left: float | None, right: float | None, log: bool = False) -> float:
    if left is None or right is None:
        return 0.0
    if log:
        left, right = math.log1p(max(left, 0)), math.log1p(max(right, 0))
    return max(0.0, 1 - abs(left - right) / max(abs(left), abs(right), 1))


class SimilarityEngine:
    def __init__(self, etfs: list[dict[str, Any]]):
        self.etfs = etfs
        corpus = [" ".join(str(item.get(key) or "") for key in ("name", "category", "strategy", "benchmark", "asset_class")) for item in etfs]
        self.matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1).fit_transform(corpus)
        self.index = {item["isin"]: index for index, item in enumerate(etfs)}

    def similar(self, isin: str, limit: int = 8) -> list[dict[str, Any]]:
        target_index = self.index.get(isin.upper())
        if target_index is None:
            return []
        target = self.etfs[target_index]
        semantic_scores = (self.matrix @ self.matrix[target_index].T).toarray().ravel()
        results = []
        for index, candidate in enumerate(self.etfs):
            if index == target_index:
                continue
            signals = {
                "semantic": float(np.clip(semantic_scores[index], 0, 1)),
                "asset_class": _same(target.get("asset_class"), candidate.get("asset_class")),
                "category": _same(target.get("category"), candidate.get("category")),
                "benchmark": _same(target.get("benchmark"), candidate.get("benchmark")),
                "currency": _same(target.get("fund_currency"), candidate.get("fund_currency")),
                "issuer": _same(target.get("issuer"), candidate.get("issuer")),
                "exchange": _overlap(target.get("exchanges", []), candidate.get("exchanges", [])),
                "aum": _numeric_proximity(target.get("aum_millions"), candidate.get("aum_millions"), log=True),
                "age": _numeric_proximity(target.get("age_years"), candidate.get("age_years")),
            }
            contributions = {key: round(signals[key] * WEIGHTS[key] * 100, 1) for key in WEIGHTS}
            score = round(sum(contributions.values()), 1)
            explanation = [
                {"signal": key.replace("_", " ").title(), "contribution": value, "detail": self._detail(key, signals[key], target, candidate)}
                for key, value in sorted(contributions.items(), key=lambda pair: pair[1], reverse=True) if value > 0
            ]
            results.append({"etf": candidate, "similarity_score": score, "explanation": explanation})
        return sorted(results, key=lambda item: item["similarity_score"], reverse=True)[:limit]

    @staticmethod
    def _detail(signal: str, value: float, target: dict[str, Any], candidate: dict[str, Any]) -> str:
        if signal == "semantic":
            return f"Name and fund characteristics have {value * 100:.0f}% text overlap."
        if signal in {"asset_class", "category", "benchmark", "currency", "issuer"}:
            field = "fund_currency" if signal == "currency" else signal
            return f"Both records use {target.get(field)}." if value else "No exact match."
        if signal == "exchange":
            return f"Exchange coverage overlap is {value * 100:.0f}%."
        if signal == "aum":
            return f"Reported AUM scale proximity is {value * 100:.0f}%."
        return f"Fund-age proximity is {value * 100:.0f}%."
