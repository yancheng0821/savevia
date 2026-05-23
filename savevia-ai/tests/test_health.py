async def test_health_endpoint_returns_ok(http_client):
    response = await http_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "savevia-ai"
    assert "version" in body


async def test_root_redirects_to_docs(http_client):
    response = await http_client.get("/", follow_redirects=False)
    assert response.status_code in (200, 307, 308)
