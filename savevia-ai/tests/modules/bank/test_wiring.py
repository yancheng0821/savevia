async def test_bank_routes_registered():
    from app.main import create_app
    app = create_app()
    paths = {r.path for r in app.routes}
    assert "/api/v1/optimize/bank/connections" in paths
    assert "/api/v1/optimize/bank/connect" in paths
    assert "/api/v1/optimize/bank/flinks-config" in paths
    assert "/api/v1/optimize/bank/connection-limit" in paths
    assert "/api/v1/optimize/bank/connections/{connection_id}" in paths
    assert "/api/v1/optimize/bank/connections/{connection_id}/refresh" in paths
    assert "/api/v1/optimize/bank/connections/{connection_id}/resync" in paths
