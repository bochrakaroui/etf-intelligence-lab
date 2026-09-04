from app.services.history import snapshot_diff


def test_snapshot_diff_detects_added_and_changed_entities():
    before = [{"isin": "A", "name": "Fund A", "issuer": "X", "asset_class": "Equity", "ter": 0.2, "aum_millions": 100, "aum_currency": "EUR"}]
    after = [{**before[0], "aum_millions": 120}, {"isin": "B", "name": "Fund B", "issuer": "Y", "asset_class": "Bond", "ter": 0.1, "aum_millions": 10, "aum_currency": "EUR"}]
    result = snapshot_diff(before, after, "2026-01-01", "2026-02-01")
    assert result["added_count"] == 1
    assert result["changed_count"] == 1
    assert result["listing_count_delta"] == 1
