from fastapi.testclient import TestClient

from app.main import app


def test_health_and_core_routes():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        listing = client.get("/api/etfs", params={"page_size": 3})
        assert listing.status_code == 200
        payload = listing.json()
        assert payload["total"] >= 200
        assert len(payload["items"]) == 3
        isin = payload["items"][0]["isin"]
        assert client.get(f"/api/etfs/{isin}").status_code == 200
        similar = client.get(f"/api/etfs/{isin}/similar").json()
        assert similar["items"] and similar["items"][0]["explanation"]
        assert client.get("/api/providers").status_code == 200
        assert client.get("/api/anomalies").status_code == 200
        assert client.get("/api/history/diff", params={"from_date": "2026-08-14", "to_date": "2026-08-28"}).status_code == 200


def test_compare_validation_and_copilot():
    with TestClient(app) as client:
        rows = client.get("/api/etfs", params={"page_size": 2}).json()["items"]
        values = ",".join(item["isin"] for item in rows)
        comparison = client.get("/api/compare", params={"isins": values})
        assert comparison.status_code == 200
        assert "approximately" in comparison.json()["summary"]
        answer = client.post("/api/copilot", json={"question": "Show the five largest ETFs"})
        assert answer.status_code == 200
        assert answer.json()["intent"] == "get_largest_etfs"
