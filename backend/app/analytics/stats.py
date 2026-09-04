from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def dataset_stats(etfs: list[dict[str, Any]], listings: list[dict[str, Any]], anomalies: list[dict[str, Any]]) -> dict[str, Any]:
    issuers = Counter(item["issuer"] for item in etfs)
    exchange_counts = Counter(item["exchange"] for item in listings)
    currency_counts = Counter(item["trading_currency"] for item in listings)
    aum_by_issuer: dict[str, float] = defaultdict(float)
    for item in etfs:
        if item.get("aum_millions") is not None:
            aum_by_issuer[item["issuer"]] += float(item["aum_millions"])
    round(sum(item["quality_score"] for item in etfs) / max(len(etfs), 1), 1)
    completeness = round(sum(1 for item in etfs if item.get("aum_millions") is not None and item.get("ter") is not None) / max(len(etfs), 1) * 100, 1)
    total_aum = sum(float(item.get("aum_millions") or 0) for item in etfs)
    components = {
        "completeness": round(completeness),
        "freshness": round(sum(item["quality"]["freshness"] for item in etfs) / max(len(etfs), 1)),
        "consistency": round(sum(item["quality"]["consistency"] for item in etfs) / max(len(etfs), 1)),
        "uniqueness": round((1 - max(0, len(listings) - len({(x['isin'], x['exchange_code'], x['ticker']) for x in listings})) / max(len(listings), 1)) * 100),
        "validity": round(sum(item["quality"]["identifier"] for item in etfs) / max(len(etfs), 1)),
    }
    return {
        "mode": "demo",
        "synthetic": True,
        "etfs_tracked": len(etfs),
        "unique_isins": len({item["isin"] for item in etfs}),
        "listing_count": len(listings),
        "issuer_count": len(issuers),
        "exchange_count": len(exchange_counts),
        "total_reported_aum_millions": round(total_aum, 2),
        "latest_snapshot": max(item["snapshot_date"] for item in etfs),
        "overall_completeness": completeness,
        "anomaly_count": len(anomalies),
        "dataset_health": round(sum(components.values()) / len(components)),
        "health_components": components,
        "aum_by_issuer": [{"name": name, "value": round(value, 2)} for name, value in sorted(aum_by_issuer.items(), key=lambda pair: pair[1], reverse=True)],
        "etfs_by_issuer": [{"name": name, "value": value} for name, value in issuers.most_common()],
        "listings_by_exchange": [{"name": name, "value": value} for name, value in exchange_counts.most_common()],
        "listings_by_currency": [{"name": name, "value": value} for name, value in currency_counts.most_common()],
        "largest_etfs": sorted(etfs, key=lambda item: item.get("aum_millions") or 0, reverse=True)[:8],
        "newest_etfs": sorted(etfs, key=lambda item: item.get("inception_date") or "0000")[-6:][::-1],
        "oldest_etfs": sorted(etfs, key=lambda item: item.get("inception_date") or "9999")[:6],
    }


def automated_insights(stats: dict[str, Any], providers: list[dict[str, Any]]) -> list[str]:
    leading = stats["aum_by_issuer"][0]
    share = leading["value"] / max(stats["total_reported_aum_millions"], 1) * 100
    currency = stats["listings_by_currency"][0]
    currency_share = currency["value"] / max(stats["listing_count"], 1) * 100
    weakest = min(providers, key=lambda item: item["reliability_score"])
    return [
        f"{leading['name']} represents {share:.1f}% of reported tracked AUM.",
        f"{currency['name']}-denominated listings account for {currency_share:.1f}% of exchange listings.",
        f"{stats['anomaly_count']} explained anomalies need review in the latest snapshot.",
        f"{weakest['provider']} has the lowest current provider reliability score at {weakest['reliability_score']}/100.",
    ]
