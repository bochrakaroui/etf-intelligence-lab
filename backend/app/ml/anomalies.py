from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import date
from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest

from app.data_quality.rules import validate_listing


def _id(*parts: Any) -> str:
    return hashlib.sha1(":".join(map(str, parts)).encode(), usedforsecurity=False).hexdigest()[:12]


def detect_anomalies(etfs: list[dict[str, Any]], listings: list[dict[str, Any]], today: date | None = None) -> list[dict[str, Any]]:
    today = today or date.today()
    snapshot = max(item["snapshot_date"] for item in etfs)
    anomalies: list[dict[str, Any]] = []
    keys = Counter((row["isin"], row["exchange_code"], row["ticker"]) for row in listings)
    for key, count in keys.items():
        if count > 1:
            anomalies.append({"id": _id("duplicate", *key), "isin": key[0], "provider": None, "anomaly_type": "duplicate_listing", "severity": "high", "title": "Duplicate listing key", "explanation": "The same ISIN, exchange and ticker appears more than once in the current snapshot.", "observed": f"{count} rows", "expected": "1 row", "snapshot_date": snapshot, "method": "deterministic_rule"})
    for row in listings:
        for failure in validate_listing(row, today=today):
            anomalies.append({"id": _id(failure["rule"], row["isin"], row["ticker"]), "isin": row["isin"], "provider": row.get("provider"), "anomaly_type": failure["rule"], "severity": "high" if failure["rule"] in {"valid_isin", "not_future"} else "medium", "title": failure["message"], "explanation": f"Validation rule `{failure['rule']}` failed for {failure['field']}.", "observed": str(row.get(failure["field"])), "expected": "valid normalized value", "snapshot_date": snapshot, "method": "deterministic_rule"})
    for etf in etfs:
        if etf.get("aum_millions") is None:
            anomalies.append({"id": _id("missing_aum", etf["isin"]), "isin": etf["isin"], "provider": etf.get("provider"), "anomaly_type": "missing_aum", "severity": "medium", "title": "AUM is unavailable", "explanation": "No reported AUM is available in the latest normalized snapshot.", "observed": "missing", "expected": "positive reported AUM", "snapshot_date": snapshot, "method": "deterministic_rule"})
        elif float(etf["aum_millions"]) == 0:
            anomalies.append({"id": _id("zero_aum", etf["isin"]), "isin": etf["isin"], "provider": etf.get("provider"), "anomaly_type": "zero_aum", "severity": "high", "title": "Suspicious zero AUM", "explanation": "A live multi-listing ETF reports exactly zero AUM, which commonly indicates a source placeholder.", "observed": "0 million", "expected": "positive reported AUM or explicit unavailable marker", "snapshot_date": snapshot, "method": "deterministic_rule"})
        if etf.get("listing_count", 0) >= 8:
            anomalies.append({"id": _id("listing_count", etf["isin"]), "isin": etf["isin"], "provider": etf.get("provider"), "anomaly_type": "listing_count", "severity": "low", "title": "Unusually broad exchange coverage", "explanation": "The fund has materially more listings than the demo-universe norm.", "observed": f"{etf['listing_count']} listings", "expected": "1–5 listings", "snapshot_date": snapshot, "method": "deterministic_rule"})
    eligible = [item for item in etfs if item.get("aum_millions") is not None]
    if len(eligible) >= 20:
        matrix = np.array([[np.log1p(max(float(item["aum_millions"]), 0)), float(item.get("ter") or 0), float(item.get("age_years") or 0), float(item.get("listing_count") or 0)] for item in eligible])
        model = IsolationForest(contamination=0.025, random_state=42, n_estimators=120)
        labels = model.fit_predict(matrix)
        medians = np.median(matrix, axis=0)
        names = ["log AUM", "TER", "fund age", "listing count"]
        for item, values, label in zip(eligible, matrix, labels, strict=True):
            if label != -1 or any(a["isin"] == item["isin"] and a["severity"] == "high" for a in anomalies):
                continue
            index = int(np.argmax(np.abs(values - medians)))
            anomalies.append({"id": _id("isolation_forest", item["isin"]), "isin": item["isin"], "provider": item.get("provider"), "anomaly_type": "unusual_profile", "severity": "low", "title": "Unusual multivariate profile", "explanation": f"Isolation Forest marked this record unusual; {names[index]} contributes the largest standardized distance from the dataset median.", "observed": f"{names[index]}={values[index]:.2f}", "expected": f"dataset median={medians[index]:.2f}", "snapshot_date": snapshot, "method": "isolation_forest"})
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(anomalies, key=lambda item: (order[item["severity"]], item["title"], item.get("isin") or ""))


def provider_quality(etfs: list[dict[str, Any]], anomalies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in etfs:
        grouped[item.get("provider") or "Unknown"].append(item)
    anomaly_counts = Counter(item.get("provider") for item in anomalies)
    output = []
    for provider, items in grouped.items():
        count = len(items)
        completeness = sum(1 for item in items if item.get("aum_millions") is not None and item.get("ter") is not None) / count * 100
        freshness = sum(item["quality"]["freshness"] for item in items) / count
        consistency = sum(item["quality"]["consistency"] for item in items) / count
        uniqueness = 100.0
        validity = sum(item["quality"]["identifier"] for item in items) / count
        anomaly_rate = anomaly_counts[provider] / count * 100
        score = round(completeness * 0.30 + freshness * 0.25 + consistency * 0.15 + uniqueness * 0.10 + validity * 0.15 + max(0, 100 - anomaly_rate) * 0.05)
        output.append({"provider": provider, "reliability_score": score, "completeness": round(completeness, 1), "freshness": round(freshness, 1), "consistency": round(consistency, 1), "uniqueness": uniqueness, "validity": round(validity, 1), "anomaly_rate": round(anomaly_rate, 1), "record_count": count, "status": "excellent" if score >= 95 else "healthy" if score >= 88 else "watch" if score >= 75 else "degraded"})
    return sorted(output, key=lambda item: item["reliability_score"], reverse=True)
