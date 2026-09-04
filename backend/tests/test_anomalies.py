from datetime import date

from app.ml.anomalies import detect_anomalies


def test_zero_aum_and_duplicate_are_explained():
    etfs = [{"isin": "IE1000000663", "name": "ETF", "aum_millions": 0, "listing_count": 1, "snapshot_date": "2026-08-28", "provider": "Demo", "ter": 0.2, "age_years": 2, "quality": {"freshness": 100, "consistency": 100, "identifier": 100}}]
    listing = {"isin": "IE1000000663", "exchange_code": "XETR", "ticker": "ETF1", "trading_currency": "EUR", "listing_date": "2020-01-01", "snapshot_date": "2026-08-28", "provider": "Demo"}
    result = detect_anomalies(etfs, [listing, dict(listing)], today=date(2026, 8, 28))
    types = {item["anomaly_type"] for item in result}
    assert {"zero_aum", "duplicate_listing"}.issubset(types)
    assert all(item["explanation"] and item["expected"] for item in result)
