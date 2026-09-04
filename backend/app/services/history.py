from __future__ import annotations

from collections import defaultdict
from typing import Any


def snapshot_diff(before: list[dict[str, Any]], after: list[dict[str, Any]], before_date: str, after_date: str) -> dict[str, Any]:
    def group(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            result[row["isin"]].append(row)
        return result

    old, new = group(before), group(after)
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = []
    for isin in sorted(set(old) & set(new)):
        old_first, new_first = old[isin][0], new[isin][0]
        fields = []
        for field in ("name", "issuer", "asset_class", "ter", "aum_millions", "aum_currency"):
            if old_first.get(field) != new_first.get(field):
                fields.append({"field": field, "before": old_first.get(field), "after": new_first.get(field)})
        if len(old[isin]) != len(new[isin]):
            fields.append({"field": "listing_count", "before": len(old[isin]), "after": len(new[isin])})
        if fields:
            changed.append({"isin": isin, "name": new_first.get("name"), "changes": fields})
    old_coverage = sum(row.get("aum_millions") is not None for row in before) / max(len(before), 1) * 100
    new_coverage = sum(row.get("aum_millions") is not None for row in after) / max(len(after), 1) * 100
    return {
        "from": before_date, "to": after_date,
        "etf_count_delta": len(new) - len(old), "listing_count_delta": len(after) - len(before),
        "aum_coverage_delta": round(new_coverage - old_coverage, 2),
        "added_count": len(added), "removed_count": len(removed), "changed_count": len(changed),
        "added": [{"isin": isin, "name": new[isin][0].get("name")} for isin in added[:100]],
        "removed": [{"isin": isin, "name": old[isin][0].get("name")} for isin in removed[:100]],
        "changed": changed[:100],
    }
