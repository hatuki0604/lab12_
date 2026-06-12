from __future__ import annotations


def test_get_seed_cafes_returns_five_or_fewer_seed_items(client):
    test_client, _ = client
    response = test_client.get("/api/seed-cafes")

    assert response.status_code == 200
    payload = response.json()
    assert payload["seed_cafes"]
    assert len(payload["seed_cafes"]) <= 5
    categories = [item["category"] for item in payload["seed_cafes"]]
    assert len(categories) == len(set(categories))
    assert all(item["google_maps_url"] for item in payload["seed_cafes"])
