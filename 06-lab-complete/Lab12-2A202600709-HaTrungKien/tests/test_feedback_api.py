from __future__ import annotations


def test_feedback_appends_log(client):
    test_client, tmp_path = client
    response = test_client.post(
        "/api/feedback",
        json={
            "selected_seed_cafe_ids": ["cafe_001"],
            "cafe_id": "cafe_001",
            "feedback": "not_my_vibe",
        },
    )

    assert response.status_code == 204

    content = (tmp_path / "feedback.jsonl").read_text(encoding="utf-8")
    assert "cafe_001" in content
    assert "not_my_vibe" in content
