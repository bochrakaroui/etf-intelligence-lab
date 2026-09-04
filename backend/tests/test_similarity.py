from app.ml.similarity import SimilarityEngine


def test_similarity_prefers_matching_characteristics():
    base = {"isin": "A", "name": "Global Equity Core", "asset_class": "Equity", "category": "Global", "benchmark": "World", "fund_currency": "EUR", "issuer": "A", "exchanges": ["Xetra"], "aum_millions": 1000, "age_years": 5}
    close = {**base, "isin": "B", "name": "Global Equity Index", "issuer": "B", "aum_millions": 900}
    far = {**base, "isin": "C", "name": "Short Treasury Bond", "asset_class": "Fixed Income", "category": "Government Bond", "benchmark": "Treasury 1Y", "fund_currency": "USD", "issuer": "C", "exchanges": ["LSE"], "aum_millions": 20, "age_years": 1}
    result = SimilarityEngine([base, close, far]).similar("A")
    assert result[0]["etf"]["isin"] == "B"
    assert result[0]["similarity_score"] > result[1]["similarity_score"]
    assert sum(item["contribution"] for item in result[0]["explanation"]) == result[0]["similarity_score"]
