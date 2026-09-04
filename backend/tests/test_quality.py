from datetime import date

from app.data_quality.rules import quality_score, valid_isin_checksum, validate_listing


def test_generated_isin_is_checksum_valid():
    assert valid_isin_checksum("IE1000000663")
    assert not valid_isin_checksum("IE1000000664")


def test_quality_score_is_transparent_and_bounded():
    item = {"isin": "IE1000000663", "name": "Demo ETF", "aum_millions": 120.0, "aum_currency": "EUR", "listing_count": 2, "exchanges": ["Xetra"], "trading_currencies": ["EUR"], "snapshot_date": "2026-08-28", "provider": "Demo"}
    score, dimensions = quality_score(item, today=date(2026, 8, 29))
    assert score == 100
    assert set(dimensions) == {"identifier", "aum", "listings", "freshness", "consistency", "source_confidence"}


def test_future_listing_date_has_explanation():
    failures = validate_listing({"isin": "IE1000000663", "aum_millions": 1, "trading_currency": "EUR", "listing_date": "2026-09-30"}, today=date(2026, 9, 1))
    assert any(item["rule"] == "not_future" and "future" in item["message"] for item in failures)
